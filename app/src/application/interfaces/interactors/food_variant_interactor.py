from typing import Optional
from sqlalchemy.exc import SQLAlchemyError

from src.infrastructure.drivers.db.tables import MenuCategory
from src.domain.dto.food_variant_dto import FoodVariantResponse, PositionsResponse, PositionItem, SizeInfo, IngredientItem
from src.application.exceptions import DatabaseException, IdNotValidError
from src.application.interfaces.repositories import food_variant_repository, menu_category_repository


class GetFoodVariantInteractor:
    def __init__(self, food_variant_repository: food_variant_repository.IFoodVariantRepository):
        self._food_variant_repository = food_variant_repository

    async def __call__(self, food_id: int):
        if food_id < 1:
            raise IdNotValidError

        food = await self._food_variant_repository.get_variants_by_food_id(food_id)

        return [
            FoodVariantResponse(
                id=fv.id,
                food_id=fv.food_id,
                price=fv.price,
                ingredient_price_modifier=fv.ingredient_price_modifier,
                is_active=fv.is_active,
            )
            for fv in food
        ]


class GetMenuCategoryPositionsIngredientsInteractor:
    def __init__(
        self,
        food_variant_repository: food_variant_repository.IFoodVariantRepository,
        menu_category_repository: menu_category_repository.IMunuCategoryRepository
    ):
        self._food_variant_repository = food_variant_repository
        self._menu_category_repository = menu_category_repository

    async def __call__(self, category_id: int) -> PositionsResponse:
        if category_id < 1:
            raise IdNotValidError

        # получаю список категорий
        category: MenuCategory = await self._menu_category_repository.get_menu_category_by_id(category_id)
        category_info = await self._menu_category_repository.get_menu_category_positions(category)

        if not category_info:
            return []

        positions = []
        for food in category.foods:
            if not food.variants:
                continue

            size_info = [
                SizeInfo(
                    measure_value=int(variant.characteristics[0].measure_value) if variant.characteristics and len(variant.characteristics) > 0 else 0,
                    price=variant.price,
                    price_multiplier=float(variant.ingredient_price_modifier) if variant.ingredient_price_modifier is not None else None
                )
                for variant in food.variants
            ]

            ingredients = []
            for assoc in food.ingredient_associations or []:
                ingredient = assoc.ingredient
                # append all ingredients
                ingredients.append(
                    IngredientItem(
                        id=ingredient.id,
                        name=ingredient.name,
                        image_url=ingredient.image_url or "",
                        price=ingredient.price
                    )
                )

            positions.append(
                PositionItem(
                    id=food.id,
                    name=food.name,
                    image_url=food.image_url or "",
                    description=food.description or "",
                    measure_name=food.measure_name or "",
                    size=size_info,
                    ingredients=ingredients
                )
            ) 

        return PositionsResponse(
            positions=positions
        )
