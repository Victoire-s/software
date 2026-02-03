import pytest

from tests.routes._app_factory import make_test_app

import routes.parking_controller as parking_ctrl


class DummyParkingRepository:
    def __init__(self, _session):
        pass


class DummyParkingService:
    view_return = {"slots": 10, "slots_max": 60, "occupation_rate": 0.1667}
    config_return = {"slots_max": 60}

    last_update_args = None
    last_reset_args = None

    def __init__(self, _repo):
        pass

    async def get_parking_view(self):
        return self.view_return

    async def get_config(self):
        return self.config_return

    async def update_config(self, *, slots_max: int):
        DummyParkingService.last_update_args = {"slots_max": slots_max}
        return {"slots_max": slots_max}

    async def reset_config(self, *, slots_max: int = 60):
        DummyParkingService.last_reset_args = {"slots_max": slots_max}
        return {"slots_max": slots_max}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(parking_ctrl, "ParkingRepository", DummyParkingRepository)
    monkeypatch.setattr(parking_ctrl, "ParkingService", DummyParkingService)
    return make_test_app()


@pytest.mark.asyncio
async def test_parking_view_requires_manager_or_secretary(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/parking/view", headers=headers)
        assert res.status == 403


@pytest.mark.asyncio
async def test_parking_view_ok_for_manager(app):
    headers = {"X-User-Id": "2", "X-User-Roles": "MANAGER"}
    async with app.asgi_client as client:
        _req, res = await client.get("/parking/view", headers=headers)
        assert res.status == 200
        assert "occupation_rate" in res.json


@pytest.mark.asyncio
async def test_parking_config_requires_secretary(app):
    headers = {"X-User-Id": "2", "X-User-Roles": "MANAGER"}
    async with app.asgi_client as client:
        _req, res = await client.get("/parking/config", headers=headers)
        assert res.status == 403


@pytest.mark.asyncio
async def test_parking_config_ok_for_secretary(app):
    headers = {"X-User-Id": "99", "X-User-Roles": "SECRETAIRE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/parking/config", headers=headers)
        assert res.status == 200
        assert res.json["slots_max"] == 60


@pytest.mark.asyncio
async def test_parking_update_config_validates_body(app):
    headers = {"X-User-Id": "99", "X-User-Roles": "SECRETAIRE"}
    async with app.asgi_client as client:
        _req, res = await client.put("/parking/config", headers=headers, json={"slots_max": -1})
        assert res.status == 400
