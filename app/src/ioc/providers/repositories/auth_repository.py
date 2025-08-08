from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.auth_repository import IAuthRepository
from src.infrastructure.adapters.repositories.auth_repository import AuthRepository


class AuthRepositryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_auth_repository(
        self, session: AsyncSession
    ) -> IAuthRepository:
        return AuthRepository(session)
