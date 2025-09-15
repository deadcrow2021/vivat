from typing import List

from sqlalchemy.exc import SQLAlchemyError

from src.application.exceptions import DatabaseException, IdNotValidError
from src.domain.dto.ingredient_dto import IngredientResponse
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import ingredient_repository


class GetAllIngredientsInteractor:
    def __init__(
        self, ingredient_repository: ingredient_repository.IIngredientRepository
    ):
        self._ingredient_repository = ingredient_repository

    async def __call__(self) -> List[IngredientResponse]:
        try:
            ingredients = await self._ingredient_repository.get_available_ingredients()
            return [
                IngredientResponse(
                    id=ingredient.id,
                    name=ingredient.name,
                    price=ingredient.price,
                    image_url=ingredient.image_url
                )
                for ingredient in ingredients
            ]
        except SQLAlchemyError:
            raise DatabaseException("Failed to get all ingredients in db")


class GetMenuCategoryIngredientsInteractor:
    def __init__(
        self, ingredient_repository: ingredient_repository.IIngredientRepository
    ):
        self._ingredient_repository = ingredient_repository

    async def __call__(self, category_id: int) -> List[IngredientResponse]:
        try:
            if category_id < 1:
                raise IdNotValidError
            ingredients = await self._ingredient_repository.get_default_ingredients_by_category_id(category_id)

            return [
                IngredientResponse(
                    id=ingredient.id,
                    name=ingredient.name,
                    price=ingredient.price,
                    image_url=ingredient.image_url
                )
                for ingredient in ingredients
            ]
        
        except SQLAlchemyError:
            raise DatabaseException("Failed to get all food ingredients from menu category in db")
