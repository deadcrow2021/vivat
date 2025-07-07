from abc import abstractmethod
from typing import Protocol


class IFoodRepository(Protocol):
    @abstractmethod
    async def get_by_id(self, food_id: int) -> dict:
        raise NotImplementedError