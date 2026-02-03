from __future__ import annotations

from sqlalchemy import delete, insert, select, update, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from db import parking_config_table, spots_table


class ParkingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- CRUD config ---
    async def create_or_reset_config(self, slots_max: int = 60) -> dict:
        # On force une seule ligne id=1
        await self.session.execute(delete(parking_config_table).where(parking_config_table.c.id == 1))
        await self.session.execute(insert(parking_config_table).values(id=1, slots_max=slots_max))
        await self.session.commit()
        return await self.get_config()

    async def get_config(self) -> dict:
        row = (
            await self.session.execute(select(parking_config_table).where(parking_config_table.c.id == 1))
        ).mappings().one_or_none()

        if not row:
            # auto-create default
            await self.session.execute(insert(parking_config_table).values(id=1, slots_max=60))
            await self.session.commit()
            row = (
                await self.session.execute(select(parking_config_table).where(parking_config_table.c.id == 1))
            ).mappings().one()

        return dict(row)

    async def update_config(self, *, slots_max: int) -> dict:
        await self.session.execute(
            update(parking_config_table).where(parking_config_table.c.id == 1).values(slots_max=slots_max)
        )
        await self.session.commit()
        return await self.get_config()

    async def delete_config(self) -> bool:
        res = await self.session.execute(delete(parking_config_table).where(parking_config_table.c.id == 1))
        await self.session.commit()
        return res.rowcount > 0

    # --- Parking view / stats ---
    async def get_parking_view(self) -> dict:
        cfg = await self.get_config()

        total = (await self.session.execute(select(func.count()).select_from(spots_table))).scalar_one()
        occupied = (
            await self.session.execute(
                select(func.count()).select_from(spots_table).where(spots_table.c.is_free.is_(False))
            )
        ).scalar_one()

        electric = (
            await self.session.execute(
                select(func.count()).select_from(spots_table).where(spots_table.c.electrical.is_(True))
            )
        ).scalar_one()

        slots_max = cfg["slots_max"] or 60
        occupation_rate = (occupied / slots_max) if slots_max else 0.0

        return {
            "slots": total,
            "slots_max": slots_max,
            "occupied": occupied,
            "free": max(0, total - occupied),
            "occupation_rate": occupation_rate,
            "electric_spots": electric,
            "electric_ratio": (electric / slots_max) if slots_max else 0.0,
        }
