from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from collections.abc import Mapping

def to_jsonable(v):
    if v is None:
        return None
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, Mapping):
        return {k: to_jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [to_jsonable(x) for x in v]
    return v
