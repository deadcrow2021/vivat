from abc import abstractmethod
from typing import List, Optional, Protocol

from src.domain.dto.auth_dto import CreateUser, LoginUserRequest, LogInDTO
from src.infrastructure.drivers.db.tables import RefreshToken, User
from src.config import Config


class IAuthRepository(Protocol):
    @abstractmethod
    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def register_user(self, created_user: CreateUser, config: Config) -> User:
        raise NotImplementedError

    @abstractmethod
    async def login_user(self, login_user_request: LoginUserRequest, config: Config) -> LogInDTO:
        raise NotImplementedError

    @abstractmethod
    async def update_access_token(self, user_phone: str, refresh_token: str, config: Config) -> LogInDTO:
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_user_refresh_tokens(self, refresh_token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_refresh_token(self, phone: str) -> Optional[RefreshToken]:
        raise NotImplementedError