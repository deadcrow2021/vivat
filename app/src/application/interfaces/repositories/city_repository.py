from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.city_dto import AddCityRequest, DeleteCityResponse, UpdateCityRequest
from src.infrastructure.drivers.db.tables import City


class ICityRepository(Protocol):
    @abstractmethod
    async def get_cities(self) -> List[City]:
        raise NotImplementedError

    @abstractmethod
    async def get_city_by_id(self, city_id: int) -> City:
        raise NotImplementedError

    @abstractmethod
    async def add_city(self, city_request: AddCityRequest) -> City:
        raise NotImplementedError

    @abstractmethod
    async def update_city(self, city: City, city_request: UpdateCityRequest) -> City:
        raise NotImplementedError

    @abstractmethod
    async def delete_city(self, city: City) -> DeleteCityResponse:
        raise NotImplementedError
