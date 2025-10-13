from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import UserNotFoundError
from src.application.interfaces.repositories.users_repository import IUsersRepository
from src.infrastructure.drivers.db.tables import User
from src.config import Config


class UsersRepository(IUsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self._session.get(User, user_id)
        if not user:
            raise UserNotFoundError(id=user_id)

        return user

    async def get_user_by_phone(self, phone: str) -> User:
        stmt = (
            select(User)
            .where(
                User.phone == phone
            )
        )
        user_result = await self._session.execute(stmt)
        user = user_result.scalars().first()
        return user


    async def delete_user(self, user_id: int) -> User:
        user = await self._session.get(User, user_id)
        if not user:
            raise UserNotFoundError(id=user_id)

        user.is_removed = True

        await self._session.flush()
        return user


    async def ban_user(self, user: User):
        user.is_banned = True

        await self._session.flush()
        return user
