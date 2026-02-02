import os
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

metadata = MetaData()

hello_table = Table(
    "hello_messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("message", String(255), nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)

def get_database_url() -> str:
    # Exemple MySQL: mysql+asyncmy://user:pass@localhost:3306/parking
    # Exemple tests: sqlite+aiosqlite:///:memory:
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")

def make_engine():
    return create_async_engine(get_database_url(), pool_pre_ping=True)

def make_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)

async def init_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
