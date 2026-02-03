from __future__ import annotations

from datetime import date, datetime
from typing import Any


def to_jsonable(value: Any) -> Any:
    """Convertit récursivement datetimes/dates en string ISO pour JSON."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]

    return value
