
from src.application.interfaces.repositories import food_repository

class GetFoodInteractor:
    def __init__(
        self,
        food_repository: food_repository.IFoodRepository
    ):
        self._food_repository = food_repository