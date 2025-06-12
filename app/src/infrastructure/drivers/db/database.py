from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import PostgresConfig


def create_engine(postgres_config: PostgresConfig) -> AsyncEngine:
    return create_async_engine(
        url=postgres_config.build_dsn(),
        echo=postgres_config.debug,
        pool_size=10,
        max_overflow=5,
        pool_recycle=300,
        pool_pre_ping=True,
        pool_use_lifo=True,
    )
