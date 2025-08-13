from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.auth_dto import CreateUser
from src.infrastructure.drivers.db.tables import User
from src.config import Config



class IUsersRepository(Protocol):
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User:
        raise NotImplementedError
