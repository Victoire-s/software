from __future__ import annotations

from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage, NotFound

from routes.security import require_auth, require_roles
from repositories.user_repository import UserRepository
from services.user_service import UserService
from utils.jsonable import to_jsonable


bp_users = Blueprint("users", url_prefix="/users")


def _json_body(request) -> dict:
    return request.json or {}


@bp_users.get("/me")
@require_auth
async def me(request):
    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)

        user = await service.get_user(request.ctx.user_id)
        if not user:
            raise NotFound("User not found")
        return json(to_jsonable(user))


@bp_users.patch("/me")
@require_auth
async def patch_me(request):
    body = _json_body(request)
    allowed = {"nom", "prenom", "email", "spot_associe"}
    if not set(body.keys()).issubset(allowed):
        raise InvalidUsage(f"Only allowed fields: {sorted(allowed)}")

    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)

        updated = await service.update_user(
            request.ctx.user_id,
            nom=body.get("nom"),
            prenom=body.get("prenom"),
            email=body.get("email"),
            spot_associe=body.get("spot_associe"),
        )
        if not updated:
            raise NotFound("User not found")
        return json(to_jsonable(updated))


# -------------------- ADMIN (SECRETAIRE) --------------------

@bp_users.get("/")
@require_roles("SECRETAIRE")
async def list_users(request):
    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)
        users = await service.list_users()
        return json(to_jsonable(users))


@bp_users.post("/")
@require_roles("SECRETAIRE")
async def create_user(request):
    body = _json_body(request)

    email = body.get("email")
    nom = body.get("nom")
    prenom = body.get("prenom")
    roles = body.get("roles") or ["EMPLOYEE"]
    spot_associe = body.get("spot_associe")

    if not isinstance(email, str) or not email.strip():
        raise InvalidUsage("email is required")
    if not isinstance(nom, str) or not nom.strip():
        raise InvalidUsage("nom is required")
    if not isinstance(prenom, str) or not prenom.strip():
        raise InvalidUsage("prenom is required")
    if not isinstance(roles, list) or not all(isinstance(r, str) for r in roles):
        raise InvalidUsage("roles must be a list of strings")

    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)
        created = await service.create_user(
            email=email.strip().lower(),
            nom=nom.strip(),
            prenom=prenom.strip(),
            roles=[r.strip().upper() for r in roles],
            spot_associe=spot_associe,
        )
        return json(to_jsonable(created), status=201)


@bp_users.get("/<user_id:int>")
@require_roles("SECRETAIRE")
async def get_user(request, user_id: int):
    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)
        user = await service.get_user(user_id)
        if not user:
            raise NotFound("User not found")
        return json(to_jsonable(user))


@bp_users.patch("/<user_id:int>")
@require_roles("SECRETAIRE")
async def patch_user(request, user_id: int):
    body = _json_body(request)
    allowed = {"nom", "prenom", "email", "spot_associe"}
    if not set(body.keys()).issubset(allowed):
        raise InvalidUsage(f"Only allowed fields: {sorted(allowed)}")

    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)

        updated = await service.update_user(
            user_id,
            nom=body.get("nom"),
            prenom=body.get("prenom"),
            email=body.get("email"),
            spot_associe=body.get("spot_associe"),
        )
        if not updated:
            raise NotFound("User not found")
        return json(to_jsonable(updated))


@bp_users.delete("/<user_id:int>")
@require_roles("SECRETAIRE")
async def delete_user(request, user_id: int):
    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)
        ok = await service.delete_user(user_id)
        if not ok:
            raise NotFound("User not found")
        return json({"deleted": True})


# -------------------- ROLES (SECRETAIRE) --------------------

@bp_users.get("/<user_id:int>/roles")
@require_roles("SECRETAIRE")
async def get_roles(request, user_id: int):
    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        roles = await repo.get_roles(user_id)
        if roles is None:
            raise NotFound("User not found")
        return json({"user_id": user_id, "roles": to_jsonable(roles)})


@bp_users.put("/<user_id:int>/roles")
@require_roles("SECRETAIRE")
async def set_roles(request, user_id: int):
    body = _json_body(request)
    roles = body.get("roles")
    if not isinstance(roles, list) or not all(isinstance(r, str) for r in roles):
        raise InvalidUsage('Body must be {"roles":["EMPLOYEE",...]}')

    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)
        new_roles = await service.set_roles(user_id, [r.strip().upper() for r in roles])
        return json({"user_id": user_id, "roles": to_jsonable(new_roles)})


@bp_users.post("/<user_id:int>/roles")
@require_roles("SECRETAIRE")
async def add_role(request, user_id: int):
    body = _json_body(request)
    role = body.get("role")
    if not isinstance(role, str) or not role.strip():
        raise InvalidUsage('Body must be {"role":"MANAGER"}')

    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)
        roles = await service.add_role(user_id, role.strip().upper())
        return json({"user_id": user_id, "roles": to_jsonable(roles)})


@bp_users.delete("/<user_id:int>/roles/<role:str>")
@require_roles("SECRETAIRE")
async def remove_role(request, user_id: int, role: str):
    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)
        roles = await service.remove_role(user_id, role.strip().upper())
        return json({"user_id": user_id, "roles": to_jsonable(roles)})
