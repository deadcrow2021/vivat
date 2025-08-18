from abc import abstractmethod
from typing import List, Protocol

from src.infrastructure.drivers.db.tables import FoodCharacteristic


class IFoodCharacteristicRepository(Protocol):
    @abstractmethod
    async def add_characteristics_to_variant_by_id(
        self,
        variant_id: int,
        characteristic_value: str
    ) -> FoodCharacteristic:
        raise NotImplementedError
