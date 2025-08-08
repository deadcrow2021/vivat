from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.auth_dto import CreateUser, LoginUserRequest, TokenDTO
from src.infrastructure.drivers.db.tables import User
from src.config import Config



class IAuthRepository(Protocol):
    @abstractmethod
    async def register_user(self, created_user: CreateUser, config: Config) -> User:
        raise NotImplementedError

    @abstractmethod
    async def login_user(self, login_user_request: LoginUserRequest, config: Config) -> TokenDTO:
        raise NotImplementedError

    @abstractmethod
    async def update_access_token(self, user_phone: str, config: Config) -> TokenDTO:
        raise NotImplementedError
