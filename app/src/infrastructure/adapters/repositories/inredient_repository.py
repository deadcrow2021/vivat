from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import IngredientsNotFoundError
from src.application.interfaces.repositories.ingredient_repository import IIngredientRepository
from src.infrastructure.drivers.db.tables import Food, FoodIngredientAssociation, Ingredient


class IngredientRepository(IIngredientRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_available_ingredients(self) -> List[Ingredient]:
        stmt = select(Ingredient).where(Ingredient.is_available == True)
        stmt_result = await self._session.execute(stmt)
        ingredients = stmt_result.scalars().all()

        return ingredients


    async def get_default_ingredients_by_category_id(self, category_id: int) -> List[Ingredient]:
        stmt = (
            select(Ingredient)
            .join(
                FoodIngredientAssociation, 
                FoodIngredientAssociation.ingredient_id == Ingredient.id
            )
            .join(
                Food, 
                Food.id == FoodIngredientAssociation.food_id
            )
            .where(
                Food.category_id == category_id,
                FoodIngredientAssociation.is_default == True
            )
            .distinct()
        )
        stmt_result = await self._session.execute(stmt)
        ingredients = stmt_result.scalars().all()

        if not ingredients:
            raise IngredientsNotFoundError("Ingredients not found")

        return ingredients
