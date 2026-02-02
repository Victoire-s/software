from sanic import Sanic
from sanic.response import json
from sanic.exceptions import InvalidUsage
from sqlalchemy import insert, select

from db import make_engine, make_session_factory, init_db, hello_table

def create_app() -> Sanic:
    Sanic.test_mode = True 
    app = Sanic("parking-reservation-api")

    engine = make_engine()
    Session = make_session_factory(engine)

    @app.before_server_start
    async def setup_db(app, _loop):
        await init_db(engine)
        app.ctx.engine = engine
        app.ctx.Session = Session

    @app.after_server_stop
    async def close_db(app, _loop):
        await app.ctx.engine.dispose()

    @app.post("/hello")
    async def post_hello(request):
        payload = request.json or {}
        message = payload.get("message")

        if not isinstance(message, str) or not message.strip():
            raise InvalidUsage("Body must be JSON: {\"message\": \"...\"}")

        async with request.app.ctx.Session() as session:
            # insert
            result = await session.execute(
                insert(hello_table).values(message=message.strip())
            )
            await session.commit()

            # récupérer l'id inséré (compat MySQL/SQLite)
            inserted_id = result.inserted_primary_key[0]

            # select pour retourner ce qui est stocké
            row = (await session.execute(
                select(hello_table).where(hello_table.c.id == inserted_id)
            )).mappings().one()

        return json({"id": row["id"], "message": row["message"]})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, dev=True)
