from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.auth_dto import CreateUser
from src.infrastructure.drivers.db.tables import User
from src.config import Config



class IUsersRepository(Protocol):
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_phone(self, phone: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: int) -> User:
        raise NotImplementedError

    @abstractmethod
    async def ban_user(self, user_id: int) -> None:
        raise NotImplementedError
