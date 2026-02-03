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


def require_auth(handler):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        roles = parse_roles(request)
        if not roles:
            raise Unauthorized("Missing X-User-Roles header")
        request.ctx.user_roles = roles
        request.ctx.user_id = get_user_id(request)
        return await handler(request, *args, **kwargs)

    return wrapper


def require_roles(*required_roles: str):
    required = {r.upper() for r in required_roles}

    def decorator(handler):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            roles = parse_roles(request)
            if not roles:
                raise Unauthorized("Missing X-User-Roles header")
            if roles.isdisjoint(required):
                raise Forbidden("Insufficient role")
            request.ctx.user_roles = roles
            request.ctx.user_id = get_user_id(request)
            return await handler(request, *args, **kwargs)

        return wrapper

    return decorator
