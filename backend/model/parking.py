from __future__ import annotations

from dataclasses import dataclass
from typing import List

from spot import Spot


@dataclass(slots=True)
class Parking:
    slots: List[Spot]
    slots_max: int = 60

    def __post_init__(self) -> None:
        # si on te passe des slots déjà construits, slots_max doit coller
        if self.slots_max <= 0:
            raise ValueError("slots_max doit être > 0")
        if len(self.slots) > self.slots_max:
            raise ValueError("slots dépasse slots_max")

    @property
    def occupation_rate(self) -> float:
        """Taux d'occupation instantané basé sur free=False."""
        if self.slots_max == 0:
            return 0.0
        occupied = sum(1 for s in self.slots if not s.free)
        return occupied / self.slots_max

    @property
    def electric_spots_ratio(self) -> float:
        if self.slots_max == 0:
            return 0.0
        electric = sum(1 for s in self.slots if s.electrical)
        return electric / self.slots_max


def build_default_parking() -> Parking:
    """
    Construit A01..F10 (60 places).
    Rangées A et F électriques.
    """
    slots: list[Spot] = []
    for row in "ABCDEF":
        for n in range(1, 11):
            spot_id = f"{row}{n:02d}"
            slots.append(
                Spot(
                    id=spot_id,
                    free=True,
                    electrical=Spot.is_electric_row(row),
                )
            )
    return Parking(slots=slots, slots_max=60)
