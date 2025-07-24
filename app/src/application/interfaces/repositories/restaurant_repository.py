from abc import abstractmethod
from typing import Protocol

from src.domain.dto.restaurant_dto import (
    AddRestaurantRequest,
    AddRestaurantResponse,
    DeleteRestaurantResponse,
    GetRestaurantsResponse,
    UpdateRestaurantRequest,
)


class IRestaurantRepository(Protocol):
    @abstractmethod
    async def get_restaurants_by_city_id(self, city_id: int) -> GetRestaurantsResponse:
        raise NotImplementedError

    @abstractmethod
    async def add_restaurant_to_city_by_id(
        self, city_id: int, restaurant: AddRestaurantRequest
    ) -> AddRestaurantResponse:
        raise NotImplementedError

    @abstractmethod
    async def change_restaurant_by_id(
        self, restaurant_id: int, update_restaurant: UpdateRestaurantRequest
    ) -> AddRestaurantResponse:
        raise NotImplementedError

    @abstractmethod
    async def delete_restaurant_by_id(
        self, restaurant_id: int
    ) -> DeleteRestaurantResponse:
        raise NotImplementedError
