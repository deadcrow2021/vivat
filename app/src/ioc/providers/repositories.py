from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.food_repository import IFoodRepository
from src.infrastructure.adapters.repositories.food_repository import FoodRepository


class RepositriesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_food_repository(
        self,
        session: AsyncSession
    ) -> IFoodRepository:
        return FoodRepository(session)
