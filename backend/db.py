import os
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, DateTime, Boolean,
    ForeignKey, UniqueConstraint, func
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

metadata = MetaData()

hello_table = Table(
    "hello_messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("message", String(255), nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)


# --- USERS ---
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("nom", String(100), nullable=False),
    Column("prenom", String(100), nullable=False),
    Column("spot_associe", String(3), nullable=True),  # ex: "A01"
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)

user_roles_table = Table(
    "user_roles",
    metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(30), primary_key=True),  # MANAGER | SECRETAIRE | EMPLOYEE
    UniqueConstraint("user_id", "role", name="uq_user_role"),
)

# --- SPOTS ---
spots_table = Table(
    "spots",
    metadata,
    Column("id", String(3), primary_key=True),              # A01..F10
    Column("is_free", Boolean, nullable=False, default=True),
    Column("electrical", Boolean, nullable=False, default=False),
    Column("reserved_from", DateTime, nullable=True),
    Column("reserved_to", DateTime, nullable=True),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False),
)

# --- PARKING CONFIG (1 ligne) ---
parking_config_table = Table(
    "parking_config",
    metadata,
    Column("id", Integer, primary_key=True),                 # toujours 1
    Column("slots_max", Integer, nullable=False, default=60),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False),
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
