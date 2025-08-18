from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.user_address_repository import IUserAddressRepository
from src.infrastructure.adapters.repositories.user_address_repository import UserAddressRepository


class UserAddressRepositryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_user_address_repository(
        self, session: AsyncSession
    ) -> IUserAddressRepository:
        return UserAddressRepository(session)
