from typing import List
from src.domain.dto.ingredient_dto import IngredientResponse
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import ingredient_repository

# TODO: add exceptions
class GetAllIngredientsInteractor:
    def __init__(
        self, ingredient_repository: ingredient_repository.IIngredientRepository
    ):
        self._ingredient_repository = ingredient_repository

    async def __call__(self) -> List[IngredientResponse]:

        ingredients = (
            await self._ingredient_repository.get_available_ingredients()
        )
        return [
            IngredientResponse(
                id=ingredient.id,
                name=ingredient.name,
                price=ingredient.price,
                image_url=ingredient.image_url
            )
            for ingredient in ingredients
        ]

class GetMenuCategoryIngredientsInteractor:
    def __init__(
        self, ingredient_repository: ingredient_repository.IIngredientRepository
    ):
        self._ingredient_repository = ingredient_repository

    async def __call__(self, category_id: int) -> List[IngredientResponse]:
        ingredients = await self._ingredient_repository.get_default_ingredients_by_category_id(category_id)
        if not ingredients:
            raise ValueError("Ingredients not found")

        return [
            IngredientResponse(
                id=ingredient.id,
                name=ingredient.name,
                price=ingredient.price,
                image_url=ingredient.image_url
            )
            for ingredient in ingredients
        ]