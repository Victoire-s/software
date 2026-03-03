import pytest
from datetime import datetime, timedelta

from tests.routes._app_factory import make_test_app
import routes.reservations_controller as res_ctrl
from model.reservation import Reservation
from sanic.exceptions import InvalidUsage, Forbidden

# --- Dummies ---
class DummyUser:
    def __init__(self, uid, email, roles):
        self.id = uid
        self.email = email
        self.roles = roles
        self.spot_associe = None
        self.nom = "Test"
        self.prenom = "User"

    @property
    def is_manager(self):
        return "MANAGER" in self.roles
        
    @property
    def is_employee(self):
        return "EMPLOYEE" in self.roles
        
    @property
    def is_secretaire(self):
        return "SECRETAIRE" in self.roles
        
    def __getitem__(self, key):
        return getattr(self, key)
        
    def get(self, key, default=None):
        return getattr(self, key, default)

class DummySpot:
    def __init__(self, sid):
        self.id = sid
        self.free = True

class DummyUserRepository:
    def __init__(self, _session): pass
    async def get_by_email(self, email):
        if email == "emp@test.com":
            return DummyUser(1, "emp@test.com", {"EMPLOYEE"})
        if email == "mgr@test.com":
            return DummyUser(2, "mgr@test.com", {"MANAGER"})
        if email == "sec@test.com":
            return DummyUser(3, "sec@test.com", {"SECRETAIRE"})
        return None

class DummySpotRepository:
    def __init__(self, _session): pass
    async def get(self, sid):
        if sid == "A01":
            return DummySpot("A01")
        return None

class DummyReservationRepository:
    def __init__(self, _session): pass
    async def has_overlap(self, spot_id, start, end):
        # Pour simplifier, A01 est bloqué du 1 au 10 janvier par défaut si on teste l'overlap
        if spot_id == "A01" and start.year == 2010:
            return True
        return False
        
    async def create(self, spot_id, user_id, start, end):
        return Reservation(
            id=1, spot_id=spot_id, user_id=user_id, start_date=start, end_date=end, checked_in=False
        )
        
    async def release_unchecked(self, cutoff):
        return 1

# --- Patched Application ---
@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(res_ctrl, "UserRepository", DummyUserRepository)
    monkeypatch.setattr(res_ctrl, "SpotRepository", DummySpotRepository)
    monkeypatch.setattr(res_ctrl, "ReservationRepository", DummyReservationRepository)
    
    # Needs to be patched at the root of the blueprint or in the app factory
    # The actual make_test_app doesn't register bp_reservations... Let's use a modified factory or modify the test app directly
    def make_res_app():
        from routes.users_controller import bp_users
        import routes.reservations_controller as rc
        from sanic import Sanic
        import uuid
        Sanic.test_mode = True
        a = Sanic(f"test-res-app-{uuid.uuid4()}")
            
        class _Ctx:
            async def __aenter__(self): return object()
            async def __aexit__(self, exc_type, exc, tb): return False
        class _Fac:
            def __call__(self): return _Ctx()
            
        a.ctx.Session = _Fac()
        a.blueprint(bp_users)
        a.blueprint(rc.bp_reservations)
        return a

    return make_res_app()

# --- Tests ---
@pytest.mark.asyncio
async def test_employee_can_reserve_5_days_max(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE", "X-User-Email": "emp@test.com"}
    async with app.asgi_client as client:
        # Valid 3 days
        _, res = await client.post("/reservations/", headers=headers, json={
            "spot_id": "A01",
            "start_date": "2030-01-01T00:00:00",
            "end_date": "2030-01-03T00:00:00"
        })
        assert res.status == 201

        # Invalid 6 working days (Mon Jan 7 → Mon Jan 14 = Mon+Tue+Wed+Thu+Fri+Mon = 6)
        _, res = await client.post("/reservations/", headers=headers, json={
            "spot_id": "A01",
            "start_date": "2030-01-07T00:00:00",
            "end_date": "2030-01-14T00:00:00"
        })
        assert res.status == 403


@pytest.mark.asyncio
async def test_manager_can_reserve_30_days_max(app):
    headers = {"X-User-Id": "2", "X-User-Roles": "MANAGER", "X-User-Email": "mgr@test.com"}
    async with app.asgi_client as client:
        # Valid 20 days
        _, res = await client.post("/reservations/", headers=headers, json={
            "spot_id": "A01",
            "start_date": "2030-01-01T00:00:00",
            "end_date": "2030-01-20T00:00:00"
        })
        assert res.status == 201

        # Invalid 35 days
        _, res = await client.post("/reservations/", headers=headers, json={
            "spot_id": "A01",
            "start_date": "2030-01-01T00:00:00",
            "end_date": "2030-02-05T00:00:00"
        })
        assert res.status == 403

@pytest.mark.asyncio
async def test_overlap_prevention(app):
    headers = {"X-User-Id": "1", "X-User-Roles": "EMPLOYEE", "X-User-Email": "emp@test.com"}
    # 2010 triggers overlap in Dummy
    async with app.asgi_client as client:
        _, res = await client.post("/reservations/", headers=headers, json={
            "spot_id": "A01",
            "start_date": "2010-01-05T00:00:00",
            "end_date": "2010-01-07T00:00:00"
        })
        assert res.status == 400
        assert "already reserved" in res.json.get("error", "")
