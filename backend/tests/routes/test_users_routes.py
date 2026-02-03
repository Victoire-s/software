import pytest

from tests.routes._app_factory import make_test_app

import routes.users_controller as users_ctrl


# -------------------- DUMMIES --------------------

class DummyUserRepository:
    def __init__(self, _session):
        pass

    async def get_roles(self, user_id: int):
        if user_id == 404:
            return None
        return ["EMPLOYEE"]


class DummyUserService:
    # valeurs configurables par test
    me_return = {"id": 1, "email": "me@test.com", "nom": "Me", "prenom": "User", "roles": ["EMPLOYEE"]}
    list_return = [{"id": 1}, {"id": 2}]
    created_return = {"id": 10, "email": "a@b.com", "nom": "Dupont", "prenom": "Jean", "roles": ["EMPLOYEE"]}

    last_create_args = None

    def __init__(self, _repo):
        pass

    async def get_user(self, user_id: int):
        if user_id == 404:
            return None
        out = dict(self.me_return)
        out["id"] = user_id
        return out

    async def update_user(self, user_id: int, **kwargs):
        if user_id == 404:
            return None
        out = {"id": user_id, **{k: v for k, v in kwargs.items() if v is not None}}
        return out

    async def list_users(self):
        return self.list_return

    async def create_user(self, **kwargs):
        DummyUserService.last_create_args = kwargs
        return self.created_return

    async def delete_user(self, _user_id: int):
        return True

    async def set_roles(self, user_id: int, roles):
        return roles

    async def add_role(self, user_id: int, role: str):
        return ["EMPLOYEE", role]

    async def remove_role(self, user_id: int, role: str):
        return ["EMPLOYEE"]


# -------------------- FIXTURE APP --------------------

@pytest.fixture
def app(monkeypatch):
    # patch classes utilisées par le controller
    monkeypatch.setattr(users_ctrl, "UserRepository", DummyUserRepository)
    monkeypatch.setattr(users_ctrl, "UserService", DummyUserService)
    return make_test_app()


# -------------------- TESTS --------------------

@pytest.mark.asyncio
async def test_users_me_requires_auth(app):
    async with app.asgi_client as client:
        _req, res = await client.get("/users/me")
        assert res.status == 401


@pytest.mark.asyncio
async def test_users_me_ok(app):
    headers = {"X-User-Id": "12", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/users/me", headers=headers)
        assert res.status == 200
        body = res.json
        assert body["id"] == 12
        assert body["email"] == "me@test.com"


@pytest.mark.asyncio
async def test_users_me_not_found(app):
    headers = {"X-User-Id": "404", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/users/me", headers=headers)
        assert res.status == 404


@pytest.mark.asyncio
async def test_users_patch_me_rejects_unknown_field(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.patch("/users/me", headers=headers, json={"hack": "nope"})
        assert res.status == 400


@pytest.mark.asyncio
async def test_users_list_requires_secretary(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/users", headers=headers)
        assert res.status == 403


@pytest.mark.asyncio
async def test_users_list_ok_for_secretary(app):
    headers = {"X-User-Id": "99", "X-User-Roles": "SECRETAIRE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/users", headers=headers)
        assert res.status == 200
        assert res.json == [{"id": 1}, {"id": 2}]


@pytest.mark.asyncio
async def test_users_create_ok_for_secretary_normalizes_roles(app):
    headers = {"X-User-Id": "99", "X-User-Roles": "SECRETAIRE"}
    payload = {"email": "a@b.com", "nom": "Dupont", "prenom": "Jean", "roles": ["employee"]}

    async with app.asgi_client as client:
        _req, res = await client.post("/users", headers=headers, json=payload)
        assert res.status == 201
        assert res.json["id"] == 10

    # Vérifie qu’on a bien uppercased dans le controller
    assert DummyUserService.last_create_args["roles"] == ["EMPLOYEE"]
