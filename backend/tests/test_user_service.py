import pytest
from unittest.mock import AsyncMock

from services.user_service import UserService


@pytest.mark.asyncio
async def test_create_user_calls_repo_and_returns_value():
    repo = AsyncMock()
    repo.create.return_value = {"id": 1, "email": "a@b.com", "roles": ["EMPLOYEE"]}

    service = UserService(repo)

    result = await service.create_user(
        email="a@b.com",
        nom="Dupont",
        prenom="Jean",
        roles=["EMPLOYEE"],
        spot_associe=None,
    )

    repo.create.assert_awaited_once_with(
        email="a@b.com",
        nom="Dupont",
        prenom="Jean",
        roles=["EMPLOYEE"],
        spot_associe=None,
    )
    assert result["id"] == 1


@pytest.mark.asyncio
async def test_get_user_calls_repo():
    repo = AsyncMock()
    repo.get_by_id.return_value = {"id": 42}

    service = UserService(repo)

    result = await service.get_user(42)

    repo.get_by_id.assert_awaited_once_with(42)
    assert result["id"] == 42


@pytest.mark.asyncio
async def test_list_users_calls_repo():
    repo = AsyncMock()
    repo.list.return_value = [{"id": 1}, {"id": 2}]

    service = UserService(repo)

    result = await service.list_users()

    repo.list.assert_awaited_once_with()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_user_calls_repo():
    repo = AsyncMock()
    repo.update_user.return_value = {"id": 1, "nom": "NouveauNom"}

    service = UserService(repo)

    result = await service.update_user(
        1, nom="NouveauNom", prenom=None, email=None, spot_associe="A01"
    )

    repo.update_user.assert_awaited_once_with(
        1, nom="NouveauNom", prenom=None, email=None, spot_associe="A01"
    )
    assert result["nom"] == "NouveauNom"


@pytest.mark.asyncio
async def test_delete_user_calls_repo():
    repo = AsyncMock()
    repo.delete.return_value = True

    service = UserService(repo)

    ok = await service.delete_user(5)

    repo.delete.assert_awaited_once_with(5)
    assert ok is True


@pytest.mark.asyncio
async def test_set_roles_rejects_empty_roles():
    repo = AsyncMock()
    service = UserService(repo)

    with pytest.raises(ValueError):
        await service.set_roles(1, [])

    repo.set_roles.assert_not_awaited()


@pytest.mark.asyncio
async def test_set_roles_calls_repo():
    repo = AsyncMock()
    repo.set_roles.return_value = ["MANAGER"]

    service = UserService(repo)

    roles = await service.set_roles(1, ["MANAGER"])

    repo.set_roles.assert_awaited_once_with(1, ["MANAGER"])
    assert roles == ["MANAGER"]


@pytest.mark.asyncio
async def test_add_role_calls_repo():
    repo = AsyncMock()
    repo.add_role.return_value = ["EMPLOYEE", "SECRETAIRE"]

    service = UserService(repo)

    roles = await service.add_role(1, "SECRETAIRE")

    repo.add_role.assert_awaited_once_with(1, "SECRETAIRE")
    assert "SECRETAIRE" in roles


@pytest.mark.asyncio
async def test_remove_role_calls_repo():
    repo = AsyncMock()
    repo.remove_role.return_value = ["EMPLOYEE"]

    service = UserService(repo)

    roles = await service.remove_role(1, "MANAGER")

    repo.remove_role.assert_awaited_once_with(1, "MANAGER")
    assert roles == ["EMPLOYEE"]
