from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.city_repository import ICityRepository
from src.infrastructure.adapters.repositories.city_repository import CityRepository


class CityRepositryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_restaurant_repository(
        self, session: AsyncSession
    ) -> ICityRepository:
        return CityRepository(session)
