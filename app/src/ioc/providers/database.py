from collections.abc import AsyncIterable

from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.application.interfaces.transaction_manager import ITransactionManager
from src.infrastructure.drivers.db.database import create_engine
from src.infrastructure.drivers.db.transaction_manager import TransactionManager
from src.config import Config
from src.logger import logger


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_engine(self, config: Config) -> AsyncEngine:
        return create_engine(config.postgres)

    @provide(scope=Scope.APP)
    async def provide_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def provide_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            try:
                logger.info('start session')
                yield session
            finally:
                logger.info('close session')
                await session.close()


    transaction_manager = provide(
        source=TransactionManager, provides=ITransactionManager, scope=Scope.REQUEST
    )
