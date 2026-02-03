from __future__ import annotations
from typing import Optional, Iterable

from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # --- CRUD ---
    async def create_user(self, email: str, nom: str, prenom: str, roles: Iterable[str] = (), spot_associe: Optional[str] = None):
        return await self.user_repo.create(email=email, nom=nom, prenom=prenom, roles=roles, spot_associe=spot_associe)

    async def get_user(self, user_id: int):
        return await self.user_repo.get_by_id(user_id)

    async def list_users(self):
        return await self.user_repo.list()

    async def update_user(self, user_id: int, *, nom=None, prenom=None, email=None, spot_associe=None):
        return await self.user_repo.update_user(user_id, nom=nom, prenom=prenom, email=email, spot_associe=spot_associe)

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repo.delete(user_id)

    # --- Roles (admin-only côté routes) ---
    async def set_roles(self, user_id: int, roles: Iterable[str]):
        # ici tu peux ajouter des règles: ex interdire roles vides, etc.
        roles = list(roles)
        if not roles:
            raise ValueError("User must have at least one role")
        return await self.user_repo.set_roles(user_id, roles)

    async def add_role(self, user_id: int, role: str):
        return await self.user_repo.add_role(user_id, role)

    async def remove_role(self, user_id: int, role: str):
        return await self.user_repo.remove_role(user_id, role)
