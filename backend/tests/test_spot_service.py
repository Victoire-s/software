import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from services.spot_service import SpotService


@pytest.mark.asyncio
async def test_create_spot_calls_repo():
    repo = AsyncMock()
    repo.create.return_value = {"id": "A01", "electrical": True, "is_free": True}

    service = SpotService(repo)

    result = await service.create_spot("A01", electrical=True, is_free=True)

    repo.create.assert_awaited_once_with("A01", electrical=True, is_free=True)
    assert result["id"] == "A01"


@pytest.mark.asyncio
async def test_get_spot_calls_repo():
    repo = AsyncMock()
    repo.get.return_value = {"id": "A01"}

    service = SpotService(repo)

    result = await service.get_spot("A01")

    repo.get.assert_awaited_once_with("A01")
    assert result["id"] == "A01"


@pytest.mark.asyncio
async def test_list_spots_calls_repo():
    repo = AsyncMock()
    repo.list.return_value = [{"id": "A01"}, {"id": "B01"}]

    service = SpotService(repo)

    result = await service.list_spots()

    repo.list.assert_awaited_once_with()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_spot_calls_repo():
    repo = AsyncMock()
    repo.update_spot.return_value = {"id": "A01", "is_free": False}

    service = SpotService(repo)

    d1 = datetime(2026, 1, 1, 8, 0, 0)
    d2 = datetime(2026, 1, 1, 12, 0, 0)

    result = await service.update_spot(
        "A01",
        is_free=False,
        electrical=None,
        reserved_from=d1,
        reserved_to=d2,
    )

    repo.update_spot.assert_awaited_once_with(
        "A01",
        is_free=False,
        electrical=None,
        reserved_from=d1,
        reserved_to=d2,
    )
    assert result["is_free"] is False


@pytest.mark.asyncio
async def test_delete_spot_calls_repo():
    repo = AsyncMock()
    repo.delete.return_value = True

    service = SpotService(repo)

    ok = await service.delete_spot("A01")

    repo.delete.assert_awaited_once_with("A01")
    assert ok is True


@pytest.mark.asyncio
async def test_list_available_calls_repo():
    repo = AsyncMock()
    repo.list_available.return_value = [{"id": "A01"}]

    service = SpotService(repo)

    result = await service.list_available(electrical_required=True)

    repo.list_available.assert_awaited_once_with(electrical_required=True)
    assert result == [{"id": "A01"}]
