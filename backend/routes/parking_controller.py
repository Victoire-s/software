from __future__ import annotations

from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage

from routes.security import require_roles
from repositories.parking_repository import ParkingRepository
from services.parking_service import ParkingService


bp_parking = Blueprint("parking", url_prefix="/parking")


def _json_body(request) -> dict:
    return request.json or {}


@bp_parking.get("/view")
@require_roles("MANAGER", "SECRETAIRE")
async def view(request):
    async with request.app.ctx.Session() as session:
        repo = ParkingRepository(session)
        service = ParkingService(repo)
        return json(await service.get_parking_view())


@bp_parking.get("/config")
@require_roles("SECRETAIRE")
async def get_config(request):
    async with request.app.ctx.Session() as session:
        repo = ParkingRepository(session)
        service = ParkingService(repo)
        return json(await service.get_config())


@bp_parking.put("/config")
@require_roles("SECRETAIRE")
async def update_config(request):
    body = _json_body(request)
    slots_max = body.get("slots_max")
    if not isinstance(slots_max, int) or slots_max <= 0:
        raise InvalidUsage('Body must be {"slots_max": 60}')

    async with request.app.ctx.Session() as session:
        repo = ParkingRepository(session)
        service = ParkingService(repo)
        return json(await service.update_config(slots_max=slots_max))


@bp_parking.post("/config/reset")
@require_roles("SECRETAIRE")
async def reset_config(request):
    body = _json_body(request)
    slots_max = body.get("slots_max", 60)
    if not isinstance(slots_max, int) or slots_max <= 0:
        raise InvalidUsage('Body must be {"slots_max": 60}')

    async with request.app.ctx.Session() as session:
        repo = ParkingRepository(session)
        service = ParkingService(repo)
        return json(await service.reset_config(slots_max=slots_max))
