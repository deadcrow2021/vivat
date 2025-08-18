from abc import abstractmethod
from typing import List, Protocol

from src.infrastructure.drivers.db.tables import FoodVariant


class IFoodVariantRepository(Protocol):
    @abstractmethod
    async def get_variants_by_food_id(self, food_id: int) -> List[FoodVariant]:
        raise NotImplementedError
