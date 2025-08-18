from src.application.interfaces.repositories import food_variant_repository


class GetFoodVariantInteractor:
    def __init__(self, food_variant_repository: food_variant_repository.IFoodVariantRepository):
        self._food_variant_repository = food_variant_repository

    async def __call__(self, id: int):
        food = await self._food_variant_repository.get_variants_by_food_id(id)
        return food
