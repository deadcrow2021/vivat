from sqlalchemy.exc import SQLAlchemyError

from src.domain.dto.food_variant_dto import FoodVariantResponse
from src.application.exceptions import DatabaseException, IdNotValidError
from src.application.interfaces.repositories import food_variant_repository


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
