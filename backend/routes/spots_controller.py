from __future__ import annotations

from datetime import datetime

from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage, NotFound

from routes.security import require_auth, require_roles
from repositories.spot_repository import SpotRepository
from services.spot_service import SpotService


bp_spots = Blueprint("spots", url_prefix="/spots")


def _json_body(request) -> dict:
    return request.json or {}


def _parse_dt(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise InvalidUsage("reserved_from/reserved_to must be ISO string")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise InvalidUsage("Invalid datetime format (expected ISO 8601)")


@bp_spots.get("/available")
@require_auth
async def available(request):
    electrical_required = request.args.get("electrical_required", "0") in ("1", "true", "True")

    async with request.app.ctx.Session() as session:
        repo = SpotRepository(session)
        service = SpotService(repo)
        spots = await service.list_available(electrical_required=electrical_required)
        return json(spots)


@bp_spots.get("/")
@require_roles("SECRETAIRE")
async def list_spots(request):
    async with request.app.ctx.Session() as session:
        repo = SpotRepository(session)
        service = SpotService(repo)
        return json(await service.list_spots())


@bp_spots.get("/<spot_id:str>")
@require_auth
async def get_spot(request, spot_id: str):
    async with request.app.ctx.Session() as session:
        repo = SpotRepository(session)
        service = SpotService(repo)
        spot = await service.get_spot(spot_id)
        if not spot:
            raise NotFound("Spot not found")
        return json(spot)


@bp_spots.post("/")
@require_roles("SECRETAIRE")
async def create_spot(request):
    body = _json_body(request)
    spot_id = body.get("id")
    electrical = body.get("electrical")
    is_free = body.get("is_free", True)

    if not isinstance(spot_id, str) or not spot_id.strip():
        raise InvalidUsage("id is required")
    if not isinstance(electrical, bool):
        raise InvalidUsage("electrical must be boolean")
    if not isinstance(is_free, bool):
        raise InvalidUsage("is_free must be boolean")

    async with request.app.ctx.Session() as session:
        repo = SpotRepository(session)
        service = SpotService(repo)
        created = await service.create_spot(spot_id.strip().upper(), electrical=electrical, is_free=is_free)
        return json(created, status=201)


@bp_spots.patch("/<spot_id:str>")
@require_roles("SECRETAIRE")
async def patch_spot(request, spot_id: str):
    body = _json_body(request)

    is_free = body.get("is_free", None)
    electrical = body.get("electrical", None)
    reserved_from = _parse_dt(body.get("reserved_from"))
    reserved_to = _parse_dt(body.get("reserved_to"))

    if is_free is not None and not isinstance(is_free, bool):
        raise InvalidUsage("is_free must be boolean")
    if electrical is not None and not isinstance(electrical, bool):
        raise InvalidUsage("electrical must be boolean")

    async with request.app.ctx.Session() as session:
        repo = SpotRepository(session)
        service = SpotService(repo)
        updated = await service.update_spot(
            spot_id.strip().upper(),
            is_free=is_free,
            electrical=electrical,
            reserved_from=reserved_from,
            reserved_to=reserved_to,
        )
        if not updated:
            raise NotFound("Spot not found")
        return json(updated)


@bp_spots.delete("/<spot_id:str>")
@require_roles("SECRETAIRE")
async def delete_spot(request, spot_id: str):
    async with request.app.ctx.Session() as session:
        repo = SpotRepository(session)
        service = SpotService(repo)
        ok = await service.delete_spot(spot_id.strip().upper())
        if not ok:
            raise NotFound("Spot not found")
        return json({"deleted": True})
