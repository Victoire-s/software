import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db import metadata
from repositories.user_repository import UserRepository


@pytest_asyncio.fixture
async def session(tmp_path):
    db_file = tmp_path / "test_user_repo.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", future=True)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as s:
        yield s

    await engine.dispose()


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_get_by_id_get_by_email_list(self, session):
        repo = UserRepository(session)

        u1 = await repo.create(
            email="a@b.com",
            nom="Dupont",
            prenom="Jean",
            roles=["EMPLOYEE"],
            spot_associe=None,
        )
        assert u1["id"] is not None
        assert u1["email"] == "a@b.com"
        assert set(u1["roles"]) == {"EMPLOYEE"}

        got_id = await repo.get_by_id(u1["id"])
        assert got_id["email"] == "a@b.com"
        assert set(got_id["roles"]) == {"EMPLOYEE"}

        got_email = await repo.get_by_email("a@b.com")
        assert got_email["id"] == u1["id"]

        # 2e user
        u2 = await repo.create(
            email="m@b.com",
            nom="Martin",
            prenom="Alice",
            roles=["MANAGER", "EMPLOYEE"],
            spot_associe="A01",
        )
        assert set(u2["roles"]) == {"MANAGER", "EMPLOYEE"}
        assert u2["spot_associe"] == "A01"

        all_users = await repo.list()
        assert len(all_users) == 2
        emails = {u["email"] for u in all_users}
        assert emails == {"a@b.com", "m@b.com"}

    @pytest.mark.asyncio
    async def test_update_user(self, session):
        repo = UserRepository(session)
        u = await repo.create(email="x@y.com", nom="X", prenom="Y", roles=["EMPLOYEE"])

        updated = await repo.update_user(u["id"], nom="NouveauNom", spot_associe="F10")
        assert updated["nom"] == "NouveauNom"
        assert updated["spot_associe"] == "F10"
        assert updated["email"] == "x@y.com"

    @pytest.mark.asyncio
    async def test_roles_methods(self, session):
        repo = UserRepository(session)
        u = await repo.create(email="r@b.com", nom="Role", prenom="Test", roles=["EMPLOYEE"])

        roles = await repo.get_roles(u["id"])
        assert set(roles) == {"EMPLOYEE"}

        roles = await repo.set_roles(u["id"], ["MANAGER"])
        assert set(roles) == {"MANAGER"}

        roles = await repo.add_role(u["id"], "SECRETAIRE")
        assert set(roles) == {"MANAGER", "SECRETAIRE"}

        roles = await repo.remove_role(u["id"], "MANAGER")
        assert set(roles) == {"SECRETAIRE"}

    @pytest.mark.asyncio
    async def test_delete(self, session):
        repo = UserRepository(session)
        u = await repo.create(email="del@b.com", nom="Del", prenom="Me", roles=["EMPLOYEE"])

        ok = await repo.delete(u["id"])
        assert ok is True

        assert await repo.get_by_id(u["id"]) is None
        assert await repo.get_by_email("del@b.com") is None
