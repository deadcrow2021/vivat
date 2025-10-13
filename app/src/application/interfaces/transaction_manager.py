from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class ITransactionManager(Protocol):
    @abstractmethod
    def __init__(self, session: AsyncSession) -> None:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def transaction(self, isolation_level: str = None):
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def flush(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
