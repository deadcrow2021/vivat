from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.ingredient_repository import (
    IIngredientRepository
)
from src.infrastructure.drivers.db.tables import Ingredient


class IngredientRepository(IIngredientRepository): # TODO: add exceptions
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_available_ingredients(self) -> List[Ingredient]:
        stmt = select(Ingredient).where(Ingredient.is_available == True)
        stmt_result = await self._session.execute(stmt)
        ingredients = stmt_result.scalars().all()
        # if not ingredients:
        #     raise CityNotFoundError()
        return ingredients
