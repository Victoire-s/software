import os
import asyncio
import json as pyjson

import aio_pika
from aiormq.exceptions import AMQPConnectionError

from sanic import Sanic
from sanic.response import json
from sanic.exceptions import InvalidUsage
from sanic.log import logger

from sqlalchemy import insert, select

from routes.auth_controller import bp_auth   # ✅ AJOUT
from routes.users_controller import bp_users
from routes.spots_controller import bp_spots
from routes.parking_controller import bp_parking

from db import make_engine, make_session_factory, init_db, hello_table


def create_app() -> Sanic:
    # En test, ça évite l'erreur "app name already in use"
    test_mode = os.getenv("SANIC_TEST_MODE", "0") == "1"
    if test_mode:
        Sanic.test_mode = True

    app = Sanic("parking-reservation-api")

    # ✅ REGISTER ROUTES / BLUEPRINTS HERE
    app.blueprint(bp_auth)   # ✅ AJOUT
    app.blueprint(bp_users)
    app.blueprint(bp_spots)
    app.blueprint(bp_parking)

    # --- DB ---
    engine = make_engine()
    Session = make_session_factory(engine)

    # --- RabbitMQ ---
    amqp_url = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
    queue_name = os.getenv("HELLO_QUEUE", "hello.queue")

    # Toggle MQ :
    mq_disabled = os.getenv("DISABLE_MQ", "0") == "1"
    mq_enabled = (not mq_disabled) and (not test_mode or "AMQP_URL" in os.environ)

    @app.before_server_start
    async def setup(app):
        # DB init
        await init_db(engine)
        app.ctx.engine = engine
        app.ctx.Session = Session

        # MQ init (optionnel)
        app.ctx.amqp_connection = None
        app.ctx.amqp_channel = None
        app.ctx.hello_queue = queue_name

        if not mq_enabled:
            logger.info("MQ disabled (test mode or DISABLE_MQ=1)")
            return

        retries = int(os.getenv("AMQP_RETRIES", "10"))
        delay_s = int(os.getenv("AMQP_RETRY_DELAY_S", "5"))

        connection = None
        channel = None

        while retries > 0:
            try:
                logger.info(f"Tentative de connexion à RabbitMQ ({amqp_url})...")
                connection = await aio_pika.connect_robust(amqp_url)

                channel = await connection.channel()
                await channel.declare_queue(queue_name, durable=True)

                logger.info("✅ Connecté à RabbitMQ avec succès !")
                break

            except (AMQPConnectionError, OSError) as e:
                retries -= 1
                if retries == 0:
                    logger.error("❌ Impossible de se connecter à RabbitMQ.")
                    raise e

                logger.warning(
                    f"⚠️ RabbitMQ indisponible. Nouvelle tentative dans {delay_s}s... ({retries} essais restants)"
                )
                await asyncio.sleep(delay_s)

        app.ctx.amqp_connection = connection
        app.ctx.amqp_channel = channel

    @app.after_server_stop
    async def teardown(app):
        if getattr(app.ctx, "amqp_connection", None):
            await app.ctx.amqp_connection.close()
        await app.ctx.engine.dispose()

    @app.get("/")
    async def root(_request):
        return json({"status": "ok", "service": "parking-reservation-api"})

    @app.get("/health")
    async def health(_request):
        return json({"status": "ok"})

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

        # 2) Publish RabbitMQ (si dispo)
        if request.app.ctx.amqp_channel:
            event = {"type": "HelloCreated", "id": row["id"], "message": row["message"]}

            await request.app.ctx.amqp_channel.default_exchange.publish(
                aio_pika.Message(
                    body=pyjson.dumps(event).encode("utf-8"),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=request.app.ctx.hello_queue,
            )
        else:
            logger.info("MQ not available -> skip publish")

        # 3) Réponse HTTP
        return json({"id": row["id"], "message": row["message"]})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, dev=True)
