from abc import abstractmethod
from typing import Protocol

from src.infrastructure.drivers.db.tables import City


class ICityRepository(Protocol):
    @abstractmethod
    async def get_city_by_id(self, city_id: int) -> City:
        raise NotImplementedError
