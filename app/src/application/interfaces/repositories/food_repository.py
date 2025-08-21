from abc import abstractmethod
from typing import Protocol

from src.domain.dto.food_dto import AddFoodRequest
from src.infrastructure.drivers.db.tables import Food


class IFoodRepository(Protocol):
    @abstractmethod
    async def get_by_id(self, food_id: int):
        raise NotImplementedError

    @abstractmethod
    async def add_food_to_category(
        self,
        menu_category_id: int,
        food_request: AddFoodRequest
        ) -> Food:
        raise NotImplementedError
