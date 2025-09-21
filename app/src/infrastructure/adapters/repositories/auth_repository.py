from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select, or_, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.infrastructure.exceptions import InvalidCredentialsError, UserExistsError
from src.domain.dto.auth_dto import CreateUser, LoginUserRequest, LogInDTO, UserLogInDTO
from src.logger import logger
from src.application.interfaces.repositories.auth_repository import IAuthRepository
from src.infrastructure.drivers.db.tables import RefreshToken, User
from src.config import Config, TokenConfig


class AuthRepository(IAuthRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        user_query = select(User).filter(User.phone == phone, User.is_removed == False)
        user_result = await self._session.execute(user_query)
        user = user_result.scalars().first()

        return user


    async def register_user(self, created_user: CreateUser, config: Config) -> User:
        self._raise_if_user_exists_by_phone(created_user)

        user = User(
            phone=created_user.phone
        )
        user.set_password(created_user.password, config.argon2)

        self._session.add(user)
        await self._session.flush()
        return user


    async def login_user(
        self,
        login_user_request: LoginUserRequest,
        config: Config
    ) -> LogInDTO:
        user_query = select(User).filter(User.phone == login_user_request.phone)
        user_result = await self._session.execute(user_query)
        user = user_result.scalars().first()

        if not user or not user.check_password(login_user_request.password):
            raise InvalidCredentialsError

        if user.needs_rehash():
            user.set_password(login_user_request.password, config.argon2)

        # Создание токенов
        access_token_expires = timedelta(minutes=config.token.access_token_expire_minutes)
        access_token = self._create_token(
            config.token,
            data={"sub": user.phone.e164},
            expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(days=config.token.refresh_token_expire_days)
        refresh_token = self._create_token(
            config.token,
            data={"sub": user.phone.e164},
            expires_delta=refresh_token_expires
        )

        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + refresh_token_expires
        )
        self._session.add(db_refresh_token)
        await self._session.flush()
        
        login_dto = UserLogInDTO(
                user_id=user.id,
                phone=user.phone.e164
            )

        return LogInDTO(
            user=login_dto,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )


    async def update_access_token(self, user_phone: str, refresh_token: str, config: Config) -> LogInDTO:
        user_query = select(User).filter(User.phone == user_phone)
        user_result = await self._session.execute(user_query)
        user = user_result.scalars().first()
        if not user:
            raise InvalidCredentialsError("Пользователь не найден. Неверный телефон в токене.")
        if user.is_removed:
            raise InvalidCredentialsError("Пользователь неактивен") # TODO: предусмотреть is_removed в остальных случаях

        token_query = (
            select(RefreshToken)
            .filter(
                RefreshToken.user_id == user.id,
                RefreshToken.token == refresh_token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        token_result = await self._session.execute(token_query)
        valid_refresh_token = token_result.scalars().first()

        if not valid_refresh_token:
            raise InvalidCredentialsError("Валидный refresh токен не найден.")

        access_token_expires = timedelta(minutes=config.token.access_token_expire_minutes)
        access_token = self._create_token(
            config.token,
            data={"sub": user.phone.e164},
            expires_delta=access_token_expires
        )
        login_dto = UserLogInDTO(
            user_id=user.id,
            phone=user.phone.e164
        )

        return LogInDTO(
            user=login_dto,
            access_token=access_token,
            token_type="bearer"
        )


    async def revoke_all_user_refresh_tokens(self, user_phone: str) -> int:
        user_query = select(User).filter(User.phone == user_phone)
        user_result = await self._session.execute(user_query)
        user = user_result.scalars().first()
        
        if not user:
            return 0

        token_query = (
            update(RefreshToken)
            .filter(
                RefreshToken.user_id == user.id,
                RefreshToken.is_revoked == False
            )
            .values(is_revoked=True)
        )
        token_result = await self._session.execute(token_query)

        return token_result.rowcount if token_result.rowcount > 0 else 0


    async def get_refresh_token(self, phone: str) -> Optional[RefreshToken]:
        refresh_token_query = (
            select(RefreshToken)
            .join(RefreshToken.user)
            .filter(User.phone == phone)
            .order_by(RefreshToken.id.desc())
        )
        refresh_token_result = await self._session.execute(refresh_token_query)
        refresh_token = refresh_token_result.scalars().first()

        return refresh_token


    async def _raise_if_user_exists_by_phone(self, created_user: CreateUser) -> None:
        user_phone_query = select(User).filter(User.phone == created_user.phone)
        user_result = await self._session.execute(user_phone_query)
        user = user_result.scalars().first()
        
        if user:
            raise UserExistsError(created_user.phone)


    def _create_token(self, config: TokenConfig, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)

        return encoded_jwt
