import os
import json as pyjson

import aio_pika
from sanic import Sanic
from sanic.response import json
from sanic.exceptions import InvalidUsage
from sqlalchemy import insert, select

from db import make_engine, make_session_factory, init_db, hello_table


def create_app() -> Sanic:
    # En test, ça évite l'erreur "app name already in use"
    if os.getenv("SANIC_TEST_MODE", "0") == "1":
        Sanic.test_mode = True

    app = Sanic("parking-reservation-api")

    # --- DB ---
    engine = make_engine()
    Session = make_session_factory(engine)

    # --- RabbitMQ ---
    amqp_url = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
    queue_name = os.getenv("HELLO_QUEUE", "hello.queue")

    @app.before_server_start
    async def setup(app):
        # DB init
        await init_db(engine)
        app.ctx.engine = engine
        app.ctx.Session = Session

        # MQ init
        connection = await aio_pika.connect_robust(amqp_url)
        channel = await connection.channel()
        await channel.declare_queue(queue_name, durable=True)

        app.ctx.amqp_connection = connection
        app.ctx.amqp_channel = channel
        app.ctx.hello_queue = queue_name

    @app.after_server_stop
    async def teardown(app):
        # MQ close
        if hasattr(app.ctx, "amqp_connection"):
            await app.ctx.amqp_connection.close()

        # DB close
        await app.ctx.engine.dispose()

    @app.post("/hello")
    async def post_hello(request):
        payload = request.json or {}
        message = payload.get("message")

        if not isinstance(message, str) or not message.strip():
            raise InvalidUsage('Body must be JSON: {"message":"..."}')

        # 1) Stockage DB
        async with request.app.ctx.Session() as session:
            result = await session.execute(
                insert(hello_table).values(message=message.strip())
            )
            await session.commit()

            inserted_id = result.inserted_primary_key[0]

            row = (
                await session.execute(
                    select(hello_table).where(hello_table.c.id == inserted_id)
                )
            ).mappings().one()

        # 2) Publish RabbitMQ
        event = {"type": "HelloCreated", "id": row["id"], "message": row["message"]}

        await request.app.ctx.amqp_channel.default_exchange.publish(
            aio_pika.Message(
                body=pyjson.dumps(event).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=request.app.ctx.hello_queue,  # queue name
        )

        # 3) Réponse HTTP
        return json({"id": row["id"], "message": row["message"]})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, dev=True)
