from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set

from roles import Role


@dataclass(slots=True)
class User:
    email: str
    nom: str
    prenom: str
    roles: Set[Role] = field(default_factory=set)
    spot_associe: Optional[str] = None  # ex: "A01" (si un manager a une place "habituelle")

    def __post_init__(self) -> None:
        if "@" not in self.email or "." not in self.email:
            raise ValueError("email invalide")
        if not self.nom.strip():
            raise ValueError("nom obligatoire")
        if not self.prenom.strip():
            raise ValueError("prenom obligatoire")

    @property
    def is_manager(self) -> bool:
        return Role.MANAGER in self.roles

    @property
    def is_secretaire(self) -> bool:
        return Role.SECRETAIRE in self.roles

    @property
    def is_employee(self) -> bool:
        return Role.EMPLOYEE in self.roles
