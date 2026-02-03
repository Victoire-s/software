import os
import json
import asyncio
import pytest
import aio_pika

from app import create_app

@pytest.mark.asyncio
async def test_post_hello_publishes_event_to_rabbitmq():
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["AMQP_URL"] = "amqp://guest:guest@localhost:5672/"
    os.environ["HELLO_QUEUE"] = "hello.queue"
    os.environ["SANIC_TEST_MODE"] = "1"

    # Connexion RabbitMQ pour purger + lire le message
    connection = await aio_pika.connect_robust(os.environ["AMQP_URL"])
    channel = await connection.channel()
    queue = await channel.declare_queue(os.environ["HELLO_QUEUE"], durable=True)

    # Purge pour éviter de lire un vieux message
    await queue.purge()

    app = create_app()

    async with app.asgi_client as client:
        _req, res = await client.post("/hello", json={"message": "hello rabbit"})
        assert res.status == 200

    # Lire 1 message avec timeout
    async with queue.iterator() as it:
        msg = await asyncio.wait_for(it.__anext__(), timeout=5)
        async with msg.process():
            payload = json.loads(msg.body.decode("utf-8"))

    assert payload["type"] == "HelloCreated"
    assert payload["message"] == "hello rabbit"
    assert isinstance(payload["id"], int)

    await connection.close()
