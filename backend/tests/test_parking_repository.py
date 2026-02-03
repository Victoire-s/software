import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db import metadata
from repositories.parking_repository import ParkingRepository
from repositories.spot_repository import SpotRepository


@pytest_asyncio.fixture
async def session(tmp_path):
    db_file = tmp_path / "test_parking_repo.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", future=True)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as s:
        yield s

    await engine.dispose()


class TestParkingRepository:
    @pytest.mark.asyncio
    async def test_get_config_autocreate_update_delete(self, session):
        repo = ParkingRepository(session)

        cfg = await repo.get_config()
        assert cfg["id"] == 1
        assert cfg["slots_max"] in (60, 0, 60)  # selon ta valeur par défaut

        cfg2 = await repo.update_config(slots_max=42)
        assert cfg2["slots_max"] == 42

        ok = await repo.delete_config()
        assert ok is True

        # après delete, get_config doit recréer par défaut
        cfg3 = await repo.get_config()
        assert cfg3["id"] == 1

    @pytest.mark.asyncio
    async def test_create_or_reset_config(self, session):
        repo = ParkingRepository(session)

        cfg = await repo.create_or_reset_config(slots_max=10)
        assert cfg["slots_max"] == 10

        cfg2 = await repo.create_or_reset_config(slots_max=20)
        assert cfg2["slots_max"] == 20

    @pytest.mark.asyncio
    async def test_get_parking_view(self, session):
        parking_repo = ParkingRepository(session)
        spot_repo = SpotRepository(session)

        # config: slots_max=10 (pour vérifier occupation_rate = occupied/slots_max)
        await parking_repo.create_or_reset_config(slots_max=10)

        # 4 spots: 2 occupés, 2 libres
        await spot_repo.create("A01", electrical=True, is_free=True)
        await spot_repo.create("A02", electrical=True, is_free=False)  # occupé
        await spot_repo.create("B01", electrical=False, is_free=False) # occupé
        await spot_repo.create("C01", electrical=False, is_free=True)

        view = await parking_repo.get_parking_view()
        assert view["slots"] == 4
        assert view["slots_max"] == 10
        assert view["occupied"] == 2
        assert view["free"] == 2

        # occupation_rate = occupied / slots_max = 2/10
        assert abs(view["occupation_rate"] - 0.2) < 1e-9

        # electric_spots = 2 (A01, A02) => ratio 2/10
        assert view["electric_spots"] == 2
        assert abs(view["electric_ratio"] - 0.2) < 1e-9
