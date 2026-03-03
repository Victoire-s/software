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
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from routes.auth_controller import bp_auth   # ✅ AJOUT
from routes.users_controller import bp_users
from routes.spots_controller import bp_spots
from routes.parking_controller import bp_parking
from routes.reservations_controller import bp_reservations # ✅ AJOUT

from db import make_engine, make_session_factory, init_db, hello_table


def create_app() -> Sanic:
    # En test, ça évite l'erreur "app name already in use"
    test_mode = os.getenv("SANIC_TEST_MODE", "0") == "1"
    if test_mode:
        Sanic.test_mode = True

    app = Sanic("parking-reservation-api")

    app.blueprint(bp_auth)    
    app.blueprint(bp_users)
    app.blueprint(bp_spots)
    app.blueprint(bp_parking)
    app.blueprint(bp_reservations) 

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

        # Auto-seed spots if empty
        async with app.ctx.Session() as session:
            from db import spots_table
            res = await session.execute(select(spots_table.c.id).limit(1))
            if res.first() is None:
                logger.info("Initializing DB with 60 default parking spots...")
                values = []
                for row in ['A', 'B', 'C', 'D', 'E', 'F']:
                    for i in range(1, 11):
                        spot_id = f'{row}{i:02d}'
                        electrical = True if row in ('A', 'F') else False
                        values.append({'id': spot_id, 'is_free': True, 'electrical': electrical})
                await session.execute(insert(spots_table).values(values))
                await session.commit()
                logger.info("DB seeded successfully!")

        # MQ init (optionnel)
        app.ctx.amqp_connection = None
        app.ctx.amqp_channel = None
        app.ctx.hello_queue = queue_name

        # Setup APScheduler
        app.ctx.scheduler = AsyncIOScheduler()

        async def release_expired_checkins_job():
            logger.info("Executing scheduled task: release_expired_checkins")
            try:
                # We need a session + repositories for this
                from repositories.reservation_repository import ReservationRepository
                from repositories.spot_repository import SpotRepository
                from repositories.user_repository import UserRepository
                from services.reservation_service import ReservationService
                
                async with app.ctx.Session() as session:
                    reservation_repo = ReservationRepository(session)
                    spot_repo = SpotRepository(session)
                    user_repo = UserRepository(session)
                    
                    service = ReservationService(
                        session, reservation_repo, spot_repo, user_repo, 
                        app.ctx.amqp_channel, app.ctx.hello_queue
                    )
                    await service.release_expired_checkins()
            except Exception as e:
                logger.error(f"Error in release_expired_checkins_job: {e}")

        # Add the job to run every day at 11:01 AM (to give a tiny grace period, or exactly at 11:00)
        app.ctx.scheduler.add_job(
            release_expired_checkins_job,
            'cron',
            hour=11,
            minute=0,
            id='release_expired_checkins_11am',
            replace_existing=True
        )
        app.ctx.scheduler.start()
        logger.info("APScheduler started")

        from run_background import start_cleanup_task
        app.add_task(start_cleanup_task(app))
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
        if hasattr(app.ctx, "scheduler") and app.ctx.scheduler.running:
            app.ctx.scheduler.shutdown()
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
