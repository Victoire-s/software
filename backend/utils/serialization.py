from __future__ import annotations
from datetime import datetime, date
from typing import Any


def jsonable(value: Any) -> Any:
    """Convertit récursivement les objets non JSON (datetime, etc.) en valeurs sérialisables."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [jsonable(v) for v in value]

    return value
