from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import InvalidUsage
from sqlalchemy.exc import IntegrityError

from repositories.user_repository import UserRepository
from services.user_service import UserService
from utils.jsonable import to_jsonable

bp_auth = Blueprint("auth", url_prefix="/auth")


def _json_body(request) -> dict:
    return request.json or {}


@bp_auth.post("/register")
async def register(request):
    body = _json_body(request)

    email = body.get("email")
    nom = body.get("nom")
    prenom = body.get("prenom")

    if not isinstance(email, str) or not email.strip():
        raise InvalidUsage("email is required")
    if not isinstance(nom, str) or not nom.strip():
        raise InvalidUsage("nom is required")
    if not isinstance(prenom, str) or not prenom.strip():
        raise InvalidUsage("prenom is required")

    email = email.strip().lower()

    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)

        # 1) pré-check
        existing = await service.get_user_by_email(email)
        if existing:
            return json(
                {"message": "Email already registered. Use /auth/login."},
                status=409,
            )

        # 2) create + catch DB unique
        try:
            created = await service.create_user(
                email=email,
                nom=nom.strip(),
                prenom=prenom.strip(),
                roles=["EMPLOYEE"],
                spot_associe=None,
            )
        except IntegrityError:
            await session.rollback()
            return json(
                {"message": "Email already registered. Use /auth/login."},
                status=409,
            )

        payload = {
            "user": created,
            "headers_to_use": {
                "X-User-Id": str(created["id"]),
                "X-User-Roles": ",".join(created.get("roles", [])),
            },
        }
        return json(to_jsonable(payload), status=201)


@bp_auth.post("/login")
async def login(request):
    body = _json_body(request)
    email = body.get("email")

    if not isinstance(email, str) or not email.strip():
        raise InvalidUsage("email is required")

    email = email.strip().lower()

    async with request.app.ctx.Session() as session:
        repo = UserRepository(session)
        service = UserService(repo)

        user = await service.get_user_by_email(email)
        if not user:
            return json({"message": "Invalid credentials"}, status=401)

        payload = {
            "user": user,
            "headers_to_use": {
                "X-User-Id": str(user["id"]),
                "X-User-Roles": ",".join(user.get("roles", [])),
            },
        }
        return json(to_jsonable(payload))
