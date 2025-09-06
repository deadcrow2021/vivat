from abc import abstractmethod
from typing import Optional, Protocol

from src.infrastructure.drivers.db.tables import City, Restaurant
from src.domain.dto.restaurant_dto import (
    AddRestaurantRequest,
    AddRestaurantResponse,
    DeleteRestaurantResponse,
    GetCityRestaurantsResponse,
    UpdateRestaurantRequest,
    UpdateRestaurantResponse,
)


class IRestaurantRepository(Protocol):
    @abstractmethod
    async def get_restaurant_by_id(self, restaurant_id: int) -> Restaurant:
        raise NotImplementedError

    @abstractmethod
    async def get_restaurant_by_last_user_order(self, user_id: int) -> Optional[Restaurant]:
        raise NotImplementedError

    @abstractmethod
    async def get_city_restaurants(self, city: City) -> GetCityRestaurantsResponse:
        raise NotImplementedError

    @abstractmethod
    async def add_restaurant_to_city_by_id(
        self,
        city: City,
        restaurant: AddRestaurantRequest
    ) -> AddRestaurantResponse:
        raise NotImplementedError

    @abstractmethod
    async def update_restaurant(
        self,
        restaurant: Restaurant,
        update_restaurant: UpdateRestaurantRequest
    ) -> UpdateRestaurantResponse:
        raise NotImplementedError

    @abstractmethod
    async def delete_restaurant(
        self, restaurant: Restaurant
    ) -> DeleteRestaurantResponse:
        raise NotImplementedError
