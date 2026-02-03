import os
import pytest
from app import create_app

@pytest.mark.asyncio
async def test_post_hello_stores_and_returns(tmp_path):
    db_file = tmp_path / "test_api.db"
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_file}"
    os.environ["SANIC_TEST_MODE"] = "1"
    os.environ["AMQP_RETRIES"] = "1"

    app = create_app()

    async with app.asgi_client as client:
        req, res = await client.post("/hello", json={"message": "hello"})
        assert res.status == 200

        body = res.json
        assert body["message"] == "hello"
        assert isinstance(body["id"], int)
