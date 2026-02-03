from __future__ import annotations
from datetime import datetime
from typing import Optional

from repositories.spot_repository import SpotRepository


class SpotService:
    def __init__(self, spot_repo: SpotRepository):
        self.spot_repo = spot_repo

    async def create_spot(self, spot_id: str, *, electrical: bool, is_free: bool = True):
        return await self.spot_repo.create(spot_id, electrical=electrical, is_free=is_free)

    async def get_spot(self, spot_id: str):
        return await self.spot_repo.get(spot_id)

    async def list_spots(self):
        return await self.spot_repo.list()

    async def update_spot(
        self,
        spot_id: str,
        *,
        is_free: Optional[bool] = None,
        electrical: Optional[bool] = None,
        reserved_from: Optional[datetime] = None,
        reserved_to: Optional[datetime] = None,
    ):
        return await self.spot_repo.update_spot(
            spot_id,
            is_free=is_free,
            electrical=electrical,
            reserved_from=reserved_from,
            reserved_to=reserved_to,
        )

    async def delete_spot(self, spot_id: str) -> bool:
        return await self.spot_repo.delete(spot_id)

    async def list_available(self, *, electrical_required: bool = False):
        return await self.spot_repo.list_available(electrical_required=electrical_required)
