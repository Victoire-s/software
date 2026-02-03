from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Spot:
    """
    Spot (place) de parking.
    - id : A01..F10
    - free : disponible à l'instant T
    - electrical : rangées A et F (bornes)
    - from_dt/to_dt : plage de réservation courante (optionnelle)

    Note: pour l'historique complet, il faudra une entité Reservation à part.
    """
    id: str
    free: bool
    electrical: bool
    from_dt: Optional[datetime] = None
    to_dt: Optional[datetime] = None

    def __post_init__(self) -> None:
        # Format attendu: Lettre + 2 chiffres (ex: A01)
        if len(self.id) != 3:
            raise ValueError("id spot invalide (ex: A01)")
        row = self.id[0]
        num = self.id[1:]
        if row not in "ABCDEF":
            raise ValueError("rangée invalide (A..F)")
        if not num.isdigit() or not (1 <= int(num) <= 10):
            raise ValueError("numéro invalide (01..10)")

        # Cohérence from/to
        if (self.from_dt is None) ^ (self.to_dt is None):
            raise ValueError("from_dt et to_dt doivent être définis ensemble")

        if self.from_dt and self.to_dt and self.from_dt >= self.to_dt:
            raise ValueError("from_dt doit être < to_dt")

        # Si free=True, en général pas de plage active
        if self.free and (self.from_dt or self.to_dt):
            self.from_dt = None
            self.to_dt = None

    @property
    def row(self) -> str:
        return self.id[0]

    @property
    def number(self) -> int:
        return int(self.id[1:])

    @staticmethod
    def is_electric_row(row: str) -> bool:
        return row in ("A", "F")
