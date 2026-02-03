import pytest
from datetime import datetime

from tests.routes._app_factory import make_test_app

import routes.spots_controller as spots_ctrl


class DummySpotRepository:
    def __init__(self, _session):
        pass


class DummySpotService:
    get_return = {"id": "A01", "electrical": True, "is_free": True}
    list_return = [{"id": "A01"}, {"id": "B01"}]
    available_return = [{"id": "A01"}]
    last_available_args = None

    def __init__(self, _repo):
        pass

    async def list_available(self, *, electrical_required: bool = False):
        DummySpotService.last_available_args = {"electrical_required": electrical_required}
        return self.available_return

    async def list_spots(self):
        return self.list_return

    async def get_spot(self, spot_id: str):
        if spot_id == "ZZ99":
            return None
        out = dict(self.get_return)
        out["id"] = spot_id
        return out

    async def create_spot(self, spot_id: str, *, electrical: bool, is_free: bool):
        return {"id": spot_id, "electrical": electrical, "is_free": is_free}

    async def update_spot(self, spot_id: str, **kwargs):
        if spot_id == "ZZ99":
            return None
        return {"id": spot_id, **kwargs}

    async def delete_spot(self, spot_id: str):
        return spot_id != "ZZ99"


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(spots_ctrl, "SpotRepository", DummySpotRepository)
    monkeypatch.setattr(spots_ctrl, "SpotService", DummySpotService)
    return make_test_app()


@pytest.mark.asyncio
async def test_spots_available_requires_auth(app):
    async with app.asgi_client as client:
        _req, res = await client.get("/spots/available")
        assert res.status == 401


@pytest.mark.asyncio
async def test_spots_available_ok(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/spots/available?electrical_required=1", headers=headers)
        assert res.status == 200
        assert res.json == [{"id": "A01"}]
        assert DummySpotService.last_available_args == {"electrical_required": True}


@pytest.mark.asyncio
async def test_spots_get_ok(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/spots/A01", headers=headers)
        assert res.status == 200
        assert res.json["id"] == "A01"


@pytest.mark.asyncio
async def test_spots_get_404(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.get("/spots/ZZ99", headers=headers)
        assert res.status == 404


@pytest.mark.asyncio
async def test_spots_create_requires_secretary(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE"}
    async with app.asgi_client as client:
        _req, res = await client.post("/spots", headers=headers, json={"id": "A01", "electrical": True})
        assert res.status == 403


@pytest.mark.asyncio
async def test_spots_create_ok_for_secretary(app):
    headers = {"X-User-Id": "99", "X-User-Roles": "SECRETAIRE"}
    async with app.asgi_client as client:
        _req, res = await client.post("/spots", headers=headers, json={"id": "a01", "electrical": True, "is_free": True})
        assert res.status in (200, 201)
        assert res.json["id"] == "A01"
