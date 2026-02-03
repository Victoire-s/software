from sanic import Sanic

from routes.users_controller import bp_users
from routes.spots_controller import bp_spots
from routes.parking_controller import bp_parking


class _DummySessionCtx:
    async def __aenter__(self):
        return object()

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummySessionFactory:
    def __call__(self):
        return _DummySessionCtx()


def make_test_app() -> Sanic:
    Sanic.test_mode = True
    app = Sanic("test-app")

    # Fake Session() pour que "async with app.ctx.Session() as session" marche
    app.ctx.Session = DummySessionFactory()

    app.blueprint(bp_users)
    app.blueprint(bp_spots)
    app.blueprint(bp_parking)

    return app
