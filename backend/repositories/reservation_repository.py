from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, insert, update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import reservations_table, spots_table
from model.reservation import Reservation

class ReservationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _row_to_entity(self, row) -> Reservation:
        return Reservation(
            id=row["id"],
            spot_id=row["spot_id"],
            user_id=row["user_id"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            checked_in=row["checked_in"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    async def create(self, spot_id: str, user_id: int, start_date: datetime, end_date: datetime) -> Reservation:
        result = await self.session.execute(
            insert(reservations_table).values(
                spot_id=spot_id,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                checked_in=False
            )
        )
        await self.session.commit()
        inserted_id = result.inserted_primary_key[0]
        return await self.get(inserted_id)

    async def get(self, p_id: int) -> Optional[Reservation]:
        stmt = select(reservations_table).where(reservations_table.c.id == p_id)
        res = await self.session.execute(stmt)
        row = res.mappings().first()
        if row:
            return self._row_to_entity(row)
        return None

    async def get_by_user(self, user_id: int) -> List[Reservation]:
        stmt = select(reservations_table).where(reservations_table.c.user_id == user_id)
        res = await self.session.execute(stmt)
        return [self._row_to_entity(r) for r in res.mappings().all()]

    async def check_in(self, p_id: int) -> Optional[Reservation]:
        stmt = update(reservations_table).where(reservations_table.c.id == p_id).values(checked_in=True)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get(p_id)

    async def delete(self, p_id: int) -> None:
        stmt = sql_delete(reservations_table).where(reservations_table.c.id == p_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def has_overlap(self, spot_id: str, start_date: datetime, end_date: datetime) -> bool:
        # A reservation overlaps if (r.start < new_end) AND (r.end > new_start)
        stmt = select(reservations_table).where(
            reservations_table.c.spot_id == spot_id,
            reservations_table.c.start_date < end_date,
            reservations_table.c.end_date > start_date
        )
        res = await self.session.execute(stmt)
        return res.first() is not None

    async def release_unchecked(self, before_time: datetime) -> int:
        # Release all reservations that have not checked-in and their start_date is < before_time
        # (Assuming before_time is the "11AM" threshold for today)
        stmt = update(reservations_table).where(
            reservations_table.c.checked_in == False,
            reservations_table.c.start_date < before_time
        ).values(
            # We effectively cancel them by adjusting end_date or deleting them?
            # Easiest way to free the spot is to set the end_date to now so it no longer overlaps.
            end_date=before_time
        )
        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.rowcount

    async def list_all(self) -> List[Reservation]:
        stmt = select(reservations_table)
        res = await self.session.execute(stmt)
        return [self._row_to_entity(r) for r in res.mappings().all()]
    
    async def list_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Reservation]:
        stmt = select(reservations_table).where(
            reservations_table.c.start_date < end_date,
            reservations_table.c.end_date > start_date
        )
        res = await self.session.execute(stmt)
        return [self._row_to_entity(r) for r in res.mappings().all()]
