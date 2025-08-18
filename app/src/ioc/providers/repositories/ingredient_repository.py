from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.ingredient_repository import IIngredientRepository
from src.infrastructure.adapters.repositories.inredient_repository import IngredientRepository


class IngredientRepositryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_ingredient_repository(self, session: AsyncSession) -> IIngredientRepository:
        return IngredientRepository(session)
