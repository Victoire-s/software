from __future__ import annotations
from repositories.parking_repository import ParkingRepository


class ParkingService:
    def __init__(self, parking_repo: ParkingRepository):
        self.parking_repo = parking_repo

    async def get_config(self):
        return await self.parking_repo.get_config()

    async def update_config(self, *, slots_max: int):
        return await self.parking_repo.update_config(slots_max=slots_max)

    async def reset_config(self, *, slots_max: int = 60):
        return await self.parking_repo.create_or_reset_config(slots_max=slots_max)

    async def get_parking_view(self):
        return await self.parking_repo.get_parking_view()
