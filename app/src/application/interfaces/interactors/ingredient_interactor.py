from typing import List

from sqlalchemy.exc import SQLAlchemyError

from src.application.exceptions import DatabaseException, IdNotValidError
from src.domain.dto.ingredient_dto import IngredientResponse
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import ingredient_repository
from src.config import Config


class GetAllIngredientsInteractor:
    def __init__(
        self, ingredient_repository: ingredient_repository.IIngredientRepository
    ):
        self._ingredient_repository = ingredient_repository

    async def __call__(self) -> List[IngredientResponse]:
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


class GetMenuCategoryIngredientsInteractor:
    def __init__(
        self, ingredient_repository: ingredient_repository.IIngredientRepository,
        config: Config
    ):
        self._ingredient_repository = ingredient_repository
        self._config = config

    async def __call__(self, category_id: int) -> List[IngredientResponse]:
        if category_id < 1:
            raise IdNotValidError
        ingredients = await self._ingredient_repository.get_adding_ingredients_by_category_id(category_id)

        return [
            IngredientResponse(
                id=ingredient.id,
                name=ingredient.name,
                price=ingredient.price,
                image_url=self._build_image_url(ingredient.image_url, "ingredients")
            )
            for ingredient in ingredients
        ]


    def _build_image_url(self, image_filename: str, image_type: str) -> str:
        """Универсальный метод построения URL для изображений"""
        if not image_filename:
            return ""

        # Всегда используем base_url из конфига
        base_url = self._config.app.resolved_static_files_base_url.rstrip('/')

        # Формируем полный URL
        full_url = f"{base_url}/images/{image_type}/{image_filename}"

        return full_url
