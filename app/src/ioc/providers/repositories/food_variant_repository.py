from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.food_variant_repository import IFoodVariantRepository
from src.infrastructure.adapters.repositories.food_variant_repository import FoodVariantRepository


class FoodVariantRepositryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_food_variant_repository(self, session: AsyncSession) -> IFoodVariantRepository:
        return FoodVariantRepository(session)
