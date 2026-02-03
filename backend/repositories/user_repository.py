from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db import users_table, user_roles_table


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # -------- CRUD --------

    async def create(
        self,
        email: str,
        nom: str,
        prenom: str,
        roles: Iterable[str] = (),
        spot_associe: Optional[str] = None,
    ) -> dict:
        res = await self.session.execute(
            insert(users_table).values(
                email=email,
                nom=nom,
                prenom=prenom,
                spot_associe=spot_associe,
            )
        )
        await self.session.commit()
        user_id = res.inserted_primary_key[0]

        if roles:
            await self.set_roles(user_id, roles)

        return await self.get_by_id(user_id)

    async def get_by_id(self, user_id: int) -> Optional[dict]:
        user_row = (
            await self.session.execute(
                select(users_table).where(users_table.c.id == user_id)
            )
        ).mappings().one_or_none()

        if not user_row:
            return None

        roles = await self.get_roles(user_id)
        return {**dict(user_row), "roles": roles}

    async def get_by_email(self, email: str) -> Optional[dict]:
        user_row = (
            await self.session.execute(
                select(users_table).where(users_table.c.email == email)
            )
        ).mappings().one_or_none()

        if not user_row:
            return None

        roles = await self.get_roles(user_row["id"])
        return {**dict(user_row), "roles": roles}

    async def list(self) -> list[dict]:
        # Jointure pour récupérer users + roles en une seule requête
        rows = (
            await self.session.execute(
                select(
                    users_table.c.id,
                    users_table.c.email,
                    users_table.c.nom,
                    users_table.c.prenom,
                    users_table.c.spot_associe,
                    user_roles_table.c.role,
                ).select_from(
                    users_table.outerjoin(user_roles_table, users_table.c.id == user_roles_table.c.user_id)
                )
            )
        ).mappings().all()

        by_id: dict[int, dict] = {}
        for r in rows:
            uid = r["id"]
            if uid not in by_id:
                by_id[uid] = {
                    "id": uid,
                    "email": r["email"],
                    "nom": r["nom"],
                    "prenom": r["prenom"],
                    "spot_associe": r["spot_associe"],
                    "roles": [],
                }
            if r["role"]:
                by_id[uid]["roles"].append(r["role"])

        return list(by_id.values())

    async def update_user(
        self,
        user_id: int,
        *,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        email: Optional[str] = None,
        spot_associe: Optional[str] = None,
    ) -> Optional[dict]:
        values = {}
        if nom is not None:
            values["nom"] = nom
        if prenom is not None:
            values["prenom"] = prenom
        if email is not None:
            values["email"] = email
        if spot_associe is not None:
            values["spot_associe"] = spot_associe

        if values:
            await self.session.execute(
                update(users_table).where(users_table.c.id == user_id).values(**values)
            )
            await self.session.commit()

        return await self.get_by_id(user_id)

    async def delete(self, user_id: int) -> bool:
        # roles -> cascade si FK ondelete CASCADE, mais on supprime quand même proprement
        await self.session.execute(delete(user_roles_table).where(user_roles_table.c.user_id == user_id))
        res = await self.session.execute(delete(users_table).where(users_table.c.id == user_id))
        await self.session.commit()
        return res.rowcount > 0

    # -------- Roles management --------

    async def get_roles(self, user_id: int) -> list[str]:
        rows = (
            await self.session.execute(
                select(user_roles_table.c.role).where(user_roles_table.c.user_id == user_id)
            )
        ).all()
        return [r[0] for r in rows]

    async def set_roles(self, user_id: int, roles: Iterable[str]) -> list[str]:
        roles = list(dict.fromkeys(roles))  # unique & stable
        await self.session.execute(delete(user_roles_table).where(user_roles_table.c.user_id == user_id))

        if roles:
            await self.session.execute(
                insert(user_roles_table),
                [{"user_id": user_id, "role": role} for role in roles],
            )

        await self.session.commit()
        return await self.get_roles(user_id)

    async def add_role(self, user_id: int, role: str) -> list[str]:
        await self.session.execute(
            insert(user_roles_table).values(user_id=user_id, role=role)
        )
        await self.session.commit()
        return await self.get_roles(user_id)

    async def remove_role(self, user_id: int, role: str) -> list[str]:
        await self.session.execute(
            delete(user_roles_table).where(
                (user_roles_table.c.user_id == user_id) & (user_roles_table.c.role == role)
            )
        )
        await self.session.commit()
        return await self.get_roles(user_id)
