from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import IngredientsNotFoundError, MenuCategoryNotFoundError
from src.application.interfaces.repositories.ingredient_repository import IIngredientRepository
from src.infrastructure.drivers.db.tables import Food, FoodIngredientAssociation, Ingredient, MenuCategory


class IngredientRepository(IIngredientRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_available_ingredients(self) -> List[Ingredient]:
        stmt = select(Ingredient).where(Ingredient.is_available == True)
        stmt_result = await self._session.execute(stmt)
        ingredients = stmt_result.scalars().all()

        return ingredients


    async def get_adding_ingredients_by_category_id(self, category_id: int) -> List[Ingredient]:
        stmt = (
            select(MenuCategory)
            .where(MenuCategory.id == category_id)
        )
        category_result = await self._session.execute(stmt)
        category = category_result.scalars().first()

        if not category:
            raise MenuCategoryNotFoundError(id=category_id)

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
                FoodIngredientAssociation.is_adding == True
            )
            .distinct()
        )
        stmt_result = await self._session.execute(stmt)
        ingredients = stmt_result.scalars().all()

        if not ingredients:
            raise IngredientsNotFoundError

        return ingredients
