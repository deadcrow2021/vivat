from abc import abstractmethod
from typing import List, Protocol

from src.infrastructure.drivers.db.tables import Ingredient


class IIngredientRepository(Protocol):
    @abstractmethod
    async def get_available_ingredients(self) -> List[Ingredient]:
        raise NotImplementedError

    @abstractmethod
    async def get_default_ingredients_by_category_id(self, category_id: int) -> List[Ingredient]:
        raise NotImplementedError
