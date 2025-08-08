from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.infrastructure.exceptions import InvalidCredentialsError, UserExistsError
from src.domain.dto.auth_dto import CreateUser, LoginUserRequest, TokenDTO
from src.logger import logger
from src.application.interfaces.repositories.auth_repository import IAuthRepository
from src.infrastructure.drivers.db.tables import User
from src.config import Config, TokenConfig


class AuthRepository(IAuthRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register_user(self, created_user: CreateUser, config: Config) -> User:
        self._raise_if_user_exists_by_phone(created_user)
        self._raise_if_user_exists_by_email(created_user)

        user = User(
            phone=created_user.phone,
            email=created_user.email,
        )
        user.set_password(created_user.password, config.argon2)

        self._session.add(user)
        await self._session.flush()
        return user


    async def login_user(self, login_user_request: LoginUserRequest, config: Config) -> TokenDTO:
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
        
        return TokenDTO(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


    async def update_access_token(self, user_phone: str, config: Config) -> TokenDTO:
        user_query = select(User).filter(User.phone == user_phone)
        user_result = await self._session.execute(user_query)
        user = user_result.scalars().first()
        
        if not user:
            raise InvalidCredentialsError("User not found. Invalid phone in token")
        
        access_token_expires = timedelta(minutes=config.token.access_token_expire_minutes)
        access_token = self._create_token(
            config.token,
            data={"sub": user.phone.e164},
            expires_delta=access_token_expires
        )

        return TokenDTO(access_token=access_token, token_type="bearer")


    async def _raise_if_user_exists_by_phone(self, created_user: CreateUser) -> None:
        user_phone_query = select(User).filter(User.phone == created_user.phone)
        user_result = await self._session.execute(user_phone_query)
        user = user_result.scalars().first()
        
        if not user:
            raise UserExistsError(created_user.phone)


    async def _raise_if_user_exists_by_email(self, created_user: CreateUser) -> None:
        user_email_query = select(User).filter(User.email == created_user.email)
        user_result = await self._session.execute(user_email_query)
        user = user_result.scalars().first()

        if not user:
            raise UserExistsError(created_user.phone)\

    def _create_token(self, config: TokenConfig, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)

        return encoded_jwt
