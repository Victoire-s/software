import pytest
from unittest.mock import AsyncMock

from services.parking_service import ParkingService


@pytest.mark.asyncio
async def test_get_config_calls_repo():
    repo = AsyncMock()
    repo.get_config.return_value = {"id": 1, "slots_max": 60}

    service = ParkingService(repo)

    result = await service.get_config()

    repo.get_config.assert_awaited_once_with()
    assert result["slots_max"] == 60


@pytest.mark.asyncio
async def test_update_config_calls_repo():
    repo = AsyncMock()
    repo.update_config.return_value = {"id": 1, "slots_max": 42}

    service = ParkingService(repo)

    result = await service.update_config(slots_max=42)

    repo.update_config.assert_awaited_once_with(slots_max=42)
    assert result["slots_max"] == 42


@pytest.mark.asyncio
async def test_reset_config_calls_repo():
    repo = AsyncMock()
    repo.create_or_reset_config.return_value = {"id": 1, "slots_max": 10}

    service = ParkingService(repo)

    result = await service.reset_config(slots_max=10)

    repo.create_or_reset_config.assert_awaited_once_with(slots_max=10)
    assert result["slots_max"] == 10


@pytest.mark.asyncio
async def test_get_parking_view_calls_repo():
    repo = AsyncMock()
    repo.get_parking_view.return_value = {"slots": 4, "slots_max": 10, "occupation_rate": 0.4}

    service = ParkingService(repo)

    result = await service.get_parking_view()

    repo.get_parking_view.assert_awaited_once_with()
    assert result["occupation_rate"] == 0.4
