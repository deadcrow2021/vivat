from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.food_characteristic_repository import IFoodCharacteristicRepository
from src.infrastructure.adapters.repositories.food_characteristic_repository import FoodCharacteristicRepository


class FoodCharacteristicRepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_food_characteristic_repository(self, session: AsyncSession) -> IFoodCharacteristicRepository:
        return FoodCharacteristicRepository(session)
