from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.restaurant_repository import (
    IRestaurantRepository,
)
from src.infrastructure.adapters.repositories.restaurant_repository import (
    RestaurantRepository,
)


class RestaurantRepositryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_restaurant_repository(
        self, session: AsyncSession
    ) -> IRestaurantRepository:
        return RestaurantRepository(session)
