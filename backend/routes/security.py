from __future__ import annotations

from functools import wraps
from sanic.exceptions import Unauthorized, Forbidden


def parse_roles(request) -> set[str]:
    raw = request.headers.get("X-User-Roles", "")
    parts = raw.replace(";", ",").split(",")
    return {p.strip().upper() for p in parts if p.strip()}


def get_user_id(request) -> int:
    raw = request.headers.get("X-User-Id")
    if not raw:
        raise Unauthorized("Missing X-User-Id header")
    try:
        return int(raw)
    except ValueError:
        raise Unauthorized("Invalid X-User-Id header")


def get_user_email(request) -> str:
    email = request.headers.get("X-User-Email", "").strip().lower()
    if not email:
        raise Unauthorized("Missing X-User-Email header")
    return email


def _populate_ctx(request):
    roles = parse_roles(request)
    if not roles:
        raise Unauthorized("Missing X-User-Roles header")
    user_id = get_user_id(request)
    email = get_user_email(request)
    request.ctx.user_roles = roles
    request.ctx.user_id = user_id
    request.ctx.user = {"id": user_id, "email": email, "roles": roles}
    return roles


def require_auth(handler):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        _populate_ctx(request)
        return await handler(request, *args, **kwargs)

    return wrapper


def require_roles(*required_roles: str):
    required = {r.upper() for r in required_roles}

    def decorator(handler):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            roles = _populate_ctx(request)
            if roles.isdisjoint(required):
                raise Forbidden("Insufficient role")
            return await handler(request, *args, **kwargs)

        return wrapper

    return decorator
