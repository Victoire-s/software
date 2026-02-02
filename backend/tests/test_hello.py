import os
import pytest
from app import create_app

@pytest.mark.asyncio
async def test_post_hello_stores_and_returns():
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

    app = create_app()

    async with app.asgi_client as client:
        req, res = await client.post("/hello", json={"message": "hello"})

        assert res.status == 200
        assert res.json["message"] == "hello"
        assert isinstance(res.json["id"], int)
