import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db import metadata
from repositories.spot_repository import SpotRepository


@pytest_asyncio.fixture
async def session(tmp_path):
    db_file = tmp_path / "test_spot_repo.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", future=True)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as s:
        yield s

    await engine.dispose()


class TestSpotRepository:
    @pytest.mark.asyncio
    async def test_create_get_list_update_delete(self, session):
        repo = SpotRepository(session)

        s1 = await repo.create("A01", electrical=True, is_free=True)
        assert s1["id"] == "A01"
        assert s1["electrical"] is True
        assert s1["is_free"] is True

        got = await repo.get("A01")
        assert got["id"] == "A01"

        all_spots = await repo.list()
        assert len(all_spots) == 1

        upd = await repo.update_spot("A01", is_free=False)
        assert upd["is_free"] is False

        ok = await repo.delete("A01")
        assert ok is True
        assert await repo.get("A01") is None

    @pytest.mark.asyncio
    async def test_list_available_filter_electrical(self, session):
        repo = SpotRepository(session)

        await repo.create("A01", electrical=True, is_free=True)
        await repo.create("B01", electrical=False, is_free=True)
        await repo.create("F10", electrical=True, is_free=False)  # occupé

        available_all = await repo.list_available(electrical_required=False)
        assert {s["id"] for s in available_all} == {"A01", "B01"}

        available_elec = await repo.list_available(electrical_required=True)
        assert {s["id"] for s in available_elec} == {"A01"}
