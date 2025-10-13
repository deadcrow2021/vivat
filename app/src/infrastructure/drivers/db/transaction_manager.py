from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from src.application.interfaces.transaction_manager import ITransactionManager
from src.logger import logger


class TransactionManager(ITransactionManager):
    def __init__(self, session: AsyncSession, engine: AsyncEngine) -> None:
        self._session = session
        self._engine = engine

    @asynccontextmanager
    async def transaction(self, isolation_level: str = None):
        if isolation_level:
            # Для специальных уровней изоляции используем connection из сессии
            async with self._engine.connect() as connection:
                connection = await connection.execution_options(isolation_level=isolation_level)
                async with connection.begin() as transaction:
                    yield connection
                    logger.info("Transaction committed successfully")
        else:
            # Обычная транзакция через сессию
            async with self._session.begin() as transaction:
                yield self._session
                logger.info("Default transaction committed successfully")


    async def commit(self) -> None:
        try:
            await self._session.commit()
            logger.info('commit')
        except Exception:
            await self._session.rollback()
            raise


    async def flush(self) -> None:
        await self._session.flush()


    async def rollback(self) -> None:
        await self._session.rollback()
