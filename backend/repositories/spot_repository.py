from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db import spots_table


class SpotRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        spot_id: str,
        *,
        electrical: bool,
        is_free: bool = True,
        reserved_from: Optional[datetime] = None,
        reserved_to: Optional[datetime] = None,
    ) -> dict:
        await self.session.execute(
            insert(spots_table).values(
                id=spot_id,
                electrical=electrical,
                is_free=is_free,
                reserved_from=reserved_from,
                reserved_to=reserved_to,
            )
        )
        await self.session.commit()
        return await self.get(spot_id)

    async def get(self, spot_id: str) -> Optional[dict]:
        row = (
            await self.session.execute(select(spots_table).where(spots_table.c.id == spot_id))
        ).mappings().one_or_none()
        return dict(row) if row else None

    async def list(self) -> list[dict]:
        rows = (await self.session.execute(select(spots_table))).mappings().all()
        return [dict(r) for r in rows]

    async def update_spot(
        self,
        spot_id: str,
        *,
        is_free: Optional[bool] = None,
        electrical: Optional[bool] = None,
        reserved_from: Optional[datetime] = None,
        reserved_to: Optional[datetime] = None,
    ) -> Optional[dict]:
        values = {}
        if is_free is not None:
            values["is_free"] = is_free
        if electrical is not None:
            values["electrical"] = electrical
        if reserved_from is not None:
            values["reserved_from"] = reserved_from
        if reserved_to is not None:
            values["reserved_to"] = reserved_to

        if values:
            await self.session.execute(
                update(spots_table).where(spots_table.c.id == spot_id).values(**values)
            )
            await self.session.commit()

        return await self.get(spot_id)

    async def delete(self, spot_id: str) -> bool:
        res = await self.session.execute(delete(spots_table).where(spots_table.c.id == spot_id))
        await self.session.commit()
        return res.rowcount > 0

    # --- helpers ---
    async def list_available(self, *, electrical_required: bool = False) -> list[dict]:
        stmt = select(spots_table).where(spots_table.c.is_free.is_(True))
        if electrical_required:
            stmt = stmt.where(spots_table.c.electrical.is_(True))

        rows = (await self.session.execute(stmt)).mappings().all()
        return [dict(r) for r in rows]
