from functools import wraps
from sanic.exceptions import Forbidden

def require_secretary(handler):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        # suppose que request.ctx.user = {"id":..., "roles":[...]}
        user = getattr(request.ctx, "user", None)
        roles = (user or {}).get("roles", [])
        if "SECRETAIRE" not in roles:
            raise Forbidden("Secretary only")
        return await handler(request, *args, **kwargs)
    return wrapper
