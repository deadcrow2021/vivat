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
