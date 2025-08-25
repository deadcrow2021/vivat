from src.domain.dto.food_dto import AddFoodRequest, AddFoodResponse
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import food_repository


class GetFoodInteractor:
    def __init__(self, food_repository: food_repository.IFoodRepository):
        self._food_repository = food_repository

    async def __call__(self, id: int):
        food = await self._food_repository.get_by_id(id)
        return food


class AddFoodInteractor:
    def __init__(
        self,
        food_repository: food_repository.IFoodRepository,
        transaction_manager: ITransactionManager
    ):
        self._food_repository = food_repository
        self._transaction_manager = transaction_manager

    async def __call__(
        self,
        menu_category_id: int,
        food_request: AddFoodRequest
    ) -> AddFoodResponse:
        food = await self._food_repository.add_food_to_category(menu_category_id, food_request)
        await self._transaction_manager.commit()

        return AddFoodResponse(
            id=food.id,
            category_id=food.category_id,
            name=food.name,
            image_url=food.image_url,
            description=food.description,
            measure_name=food.measure_name,
        )
