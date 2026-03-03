from datetime import datetime

from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage, Forbidden, NotFound

from routes.security import require_auth, require_roles
from repositories.reservation_repository import ReservationRepository
from repositories.spot_repository import SpotRepository
from repositories.user_repository import UserRepository
from services.reservation_service import ReservationService


bp_reservations = Blueprint("reservations", url_prefix="/reservations")


def _json_body(request) -> dict:
    return request.json or {}

def _jsonable(v):
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_jsonable(x) for x in v]
    # For dataclasses lacking generic __dict__
    if hasattr(v, '__slots__'):
        return {s: _jsonable(getattr(v, s)) for s in v.__slots__}
    return v

@bp_reservations.post("/")
@require_auth
async def create_reservation(request):
    body = _json_body(request)
    spot_id = body.get("spot_id")
    start_date_str = body.get("start_date")
    end_date_str = body.get("end_date")

    if not spot_id or not start_date_str or not end_date_str:
        raise InvalidUsage("spot_id, start_date and end_date are required")

    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
    except ValueError:
        raise InvalidUsage("Invalid ISO date format")

    try:
        user_email = request.ctx.user["email"]
        async with request.app.ctx.Session() as session:
            reservation_repo = ReservationRepository(session)
            spot_repo = SpotRepository(session)
            user_repo = UserRepository(session)
            
            # Reusing the AMQP channel from the app context if available
            amqp_channel = getattr(request.app.ctx, "amqp_channel", None)
            hello_queue = getattr(request.app.ctx, "hello_queue", None)

            service = ReservationService(
                session, reservation_repo, spot_repo, user_repo, amqp_channel, hello_queue
            )

            reservation = await service.create_reservation(
                spot_id.strip().upper(), user_email, start_date, end_date
            )
            return json(_jsonable(reservation), status=201)
    except (InvalidUsage, Forbidden) as e:
        return json({"error": str(e)}, status=e.status_code)
    except Exception as e:
        return json({"error": str(e)}, status=400)


@bp_reservations.get("/me")
@require_auth
async def my_reservations(request):
    user_email = request.ctx.user["email"]
    async with request.app.ctx.Session() as session:
        reservation_repo = ReservationRepository(session)
        spot_repo = SpotRepository(session)
        user_repo = UserRepository(session)
        service = ReservationService(session, reservation_repo, spot_repo, user_repo)
        
        reservations = await service.get_my_reservations(user_email)
        return json(_jsonable(reservations))


@bp_reservations.patch("/<reservation_id:int>/checkin")
@require_auth
async def checkin_reservation(request, reservation_id: int):
    user_email = request.ctx.user["email"]
    try:
        async with request.app.ctx.Session() as session:
            reservation_repo = ReservationRepository(session)
            spot_repo = SpotRepository(session)
            user_repo = UserRepository(session)
            service = ReservationService(session, reservation_repo, spot_repo, user_repo)

            checked_in = await service.check_in(reservation_id, user_email)
            return json(_jsonable(checked_in))
    except (InvalidUsage, Forbidden) as e:
        return json({"error": str(e)}, status=e.status_code)
    except Exception as e:
        return json({"error": str(e)}, status=400)


@bp_reservations.delete("/<reservation_id:int>")
@require_auth
async def cancel_reservation(request, reservation_id: int):
    user_email = request.ctx.user["email"]
    try:
        async with request.app.ctx.Session() as session:
            reservation_repo = ReservationRepository(session)
            spot_repo = SpotRepository(session)
            user_repo = UserRepository(session)
            service = ReservationService(session, reservation_repo, spot_repo, user_repo)

            await service.cancel_reservation(reservation_id, user_email)
            return json({"message": "Reservation cancelled"}, status=200)
    except (InvalidUsage, Forbidden) as e:
        return json({"error": str(e)}, status=e.status_code)
    except Exception as e:
        return json({"error": str(e)}, status=400)


@bp_reservations.post("/qr-checkin/<spot_id:str>")
@require_auth
async def qr_checkin(request, spot_id: str):
    """
    Dedicated endpoint for QR code scans. Checks in the user if they have a
    valid reservation for this spot today.
    """
    user_email = request.ctx.user["email"]
    try:
        async with request.app.ctx.Session() as session:
            reservation_repo = ReservationRepository(session)
            spot_repo = SpotRepository(session)
            user_repo = UserRepository(session)
            service = ReservationService(session, reservation_repo, spot_repo, user_repo)
            
            # Find today's active reservation for this user + spot
            my_reservations = await service.get_my_reservations(user_email)
            now = datetime.now()
            
            valid_reservation = None
            for res in my_reservations:
                if res.spot_id.upper() == spot_id.upper() and res.start_date.date() <= now.date() <= res.end_date.date():
                    valid_reservation = res
                    break
                    
            if not valid_reservation:
                raise Forbidden("No active reservation found for this spot today")
                
            if valid_reservation.checked_in:
                return json({"message": "Already checked in", "reservation": _jsonable(valid_reservation)})
                
            checked_in = await service.check_in(valid_reservation.id, user_email)
            return json(_jsonable(checked_in))
    except (InvalidUsage, Forbidden) as e:
        return json({"error": str(e)}, status=e.status_code)
    except Exception as e:
        return json({"error": str(e)}, status=400)


@bp_reservations.get("/")
@require_roles("MANAGER", "SECRETAIRE")
async def list_all(request):
    async with request.app.ctx.Session() as session:
        reservation_repo = ReservationRepository(session)
        spot_repo = SpotRepository(session)
        user_repo = UserRepository(session)
        service = ReservationService(session, reservation_repo, spot_repo, user_repo)
        
        reservations = await service.list_all()
        return json(_jsonable(reservations))
