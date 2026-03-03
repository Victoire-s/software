import json
from datetime import datetime, timedelta
from typing import List, Optional
import aio_pika

from sqlalchemy.ext.asyncio import AsyncSession
from repositories.reservation_repository import ReservationRepository
from repositories.spot_repository import SpotRepository
from repositories.user_repository import UserRepository
from model.reservation import Reservation
from sanic.exceptions import InvalidUsage, Forbidden
from sanic.log import logger


def _count_working_days(start: datetime, end: datetime) -> int:
    """Count working days (Mon–Fri) between start and end, inclusive."""
    count = 0
    current = start.date()
    end_d = end.date()
    while current <= end_d:
        if current.weekday() < 5:  # 0=Monday … 4=Friday
            count += 1
        current += timedelta(days=1)
    return count


class ReservationService:
    def __init__(self, session: AsyncSession,
                 reservation_repo: ReservationRepository,
                 spot_repo: SpotRepository,
                 user_repo: UserRepository,
                 amqp_channel=None, hello_queue=None):
        self.session = session
        self.reservation_repo = reservation_repo
        self.spot_repo = spot_repo
        self.user_repo = user_repo
        self.amqp_channel = amqp_channel
        self.hello_queue = hello_queue

    async def create_reservation(self, spot_id: str, user_email: str, start_date: datetime, end_date: datetime) -> Reservation:
        # User checks
        user = await self.user_repo.get_by_email(user_email)
        if not user:
            raise InvalidUsage("User not found")
        
        # Date checks
        if start_date >= end_date:
            raise InvalidUsage("Start date must be before end date")
        
        working_days = _count_working_days(start_date, end_date)
        calendar_days = (end_date - start_date).days + 1
        
        is_manager = "MANAGER" in user.get("roles", [])
        if is_manager:
            if calendar_days > 30:
                raise Forbidden("Managers can reserve up to 30 calendar days maximum")
        else:
            if working_days > 5:
                raise Forbidden("Employees can reserve up to 5 working days (Mon–Fri) maximum")

        # Spot checks
        spot = await self.spot_repo.get(spot_id)
        if not spot:
            raise InvalidUsage("Spot not found")

        # Overlap checks
        has_overlap = await self.reservation_repo.has_overlap(spot_id, start_date, end_date)
        if has_overlap:
            raise InvalidUsage(f"Spot {spot_id} is already reserved for these dates")

        # Create
        reservation = await self.reservation_repo.create(spot_id, user["id"], start_date, end_date)

        # Send MQ notification
        if self.amqp_channel and self.hello_queue:
            try:
                msg = {
                    "type": "ReservationCreated",
                    "user_email": user["email"],
                    "spot_id": spot_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                await self.amqp_channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(msg).encode("utf-8"),
                        content_type="application/json",
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=self.hello_queue,
                )
            except Exception as e:
                logger.error(f"Failed to publish MQ notification: {e}")

        return reservation

    async def check_in(self, reservation_id: int, user_email: str) -> Optional[Reservation]:
        user = await self.user_repo.get_by_email(user_email)
        if not user:
            raise InvalidUsage("User not found")
        
        res = await self.reservation_repo.get(reservation_id)
        if not res:
            raise InvalidUsage("Reservation not found")

        is_secretaire = "SECRETAIRE" in user.get("roles", [])
        # Allow secretaire/manager to check-in anyone? For now exact user only unless admin.
        if res.user_id != user["id"] and not is_secretaire:
            raise Forbidden("You can only check-in your own reservation")
        
        return await self.reservation_repo.check_in(reservation_id)

    async def cancel_reservation(self, reservation_id: int, user_email: str) -> bool:
        user = await self.user_repo.get_by_email(user_email)
        if not user:
            raise InvalidUsage("User not found")

        res = await self.reservation_repo.get(reservation_id)
        if not res:
            raise InvalidUsage("Reservation not found")

        # Allow user to delete their own, or an admin (Manager/Secretaire) to delete any
        roles = user.get("roles", [])
        is_admin = "MANAGER" in roles or "SECRETAIRE" in roles

        if res.user_id != user["id"] and not is_admin:
            raise Forbidden("You can only cancel your own reservation")

        await self.reservation_repo.delete(reservation_id)
        return True

    async def release_expired_checkins(self):
        # Everything starting today that is not checked-in by 11 AM will have its end_date set to Now
        now = datetime.now()
        # If today is after 11AM
        if now.hour >= 11:
            # We want to cancel any reservation that started today (or earlier) and is not checked in
            cutoff = now.replace(hour=11, minute=0, second=0, microsecond=0)
            released_count = await self.reservation_repo.release_unchecked(cutoff)
            logger.info(f"Released {released_count} unchecked reservations")
        return 0

    async def get_my_reservations(self, user_email: str) -> List[Reservation]:
        user = await self.user_repo.get_by_email(user_email)
        if not user:
            return []
        return await self.reservation_repo.get_by_user(user["id"])

    async def list_all(self) -> List[Reservation]:
        return await self.reservation_repo.list_all()
    
    async def list_active(self, start_date: datetime, end_date: datetime) -> List[Reservation]:
        return await self.reservation_repo.list_by_date_range(start_date, end_date)
