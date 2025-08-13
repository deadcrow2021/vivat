from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.adapters.repositories.users_repository import UsersRepository
from src.application.interfaces.repositories.users_repository import IUsersRepository


class UsersRepositryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_users_repository(
        self, session: AsyncSession
    ) -> IUsersRepository:
        return UsersRepository(session)
