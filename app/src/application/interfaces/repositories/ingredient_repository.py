from abc import abstractmethod
from typing import List, Protocol

from src.infrastructure.drivers.db.tables import Ingredient


class IIngredientRepository(Protocol):
    @abstractmethod
    async def get_available_ingredients(self) -> List[Ingredient]:
        raise NotImplementedError
