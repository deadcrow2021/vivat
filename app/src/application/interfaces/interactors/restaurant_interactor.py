from sqlalchemy.exc import SQLAlchemyError

from src.application.exceptions import DatabaseException, IdNotValidError
from src.domain.dto.restaurant_dto import (
    AddRestaurantRequest,
    DeleteRestaurantResponse,
    GetCityRestaurantsResponse,
    GetRestaurantResponse,
    UpdateRestaurantRequest,
    WorkingHoursModel,
)
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import restaurant_repository
from src.application.interfaces.repositories import city_repository
from src.logger import logger


class GetRestaurantInteractor:
    def __init__(
        self,
        restaurant_repository: restaurant_repository.IRestaurantRepository
    ):
        self._restaurant_repository = restaurant_repository

    async def __call__(self, restaurant_id: int) -> GetRestaurantResponse:
        if restaurant_id < 1:
            raise IdNotValidError

        restaurant = await self._restaurant_repository.get_restaurant_by_id(restaurant_id)
        return GetRestaurantResponse(
            id=restaurant.id,
            name=restaurant.name,
            phone=restaurant.phone.e164,
            address=restaurant.address,
            coords=[float(restaurant.latitude), float(restaurant.longitude)],
            working_hours=WorkingHoursModel(root=self._restaurant_repository._get_working_hours(restaurant)),
            features=self._restaurant_repository._get_features(restaurant),
            actions=self._restaurant_repository._get_allowed_actions(restaurant),
        )


class GetCityRestaurantsInteractor:
    def __init__(
        self,
        city_repository: city_repository.ICityRepository,
        restaurant_repository: restaurant_repository.IRestaurantRepository
    ):
        self._city_repository = city_repository
        self._restaurant_repository = restaurant_repository

    async def __call__(self, city_id: int) -> GetCityRestaurantsResponse:
        if city_id < 1:
            raise IdNotValidError

        city = await self._city_repository.get_city_by_id(city_id)
        restaurants_response: GetCityRestaurantsResponse = await self._restaurant_repository.get_city_restaurants(city)
        return restaurants_response


class UpdateRestaurantInteractor:
    def __init__(
        self,
        restaurant_repository: restaurant_repository.IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ):
        self._restaurant_repository = restaurant_repository
        self._transaction_manager = transaction_manager

    async def __call__(
        self,
        restaurant_id: int,
        restaurant_request: UpdateRestaurantRequest,
    ) -> None:
        if restaurant_id < 1:
            raise IdNotValidError

        restaurant = await self._restaurant_repository.get_restaurant_by_id(restaurant_id)
        restaurant_response = await self._restaurant_repository.update_restaurant(
            restaurant,
            restaurant_request
        )
        await self._transaction_manager.commit()
        return restaurant_response


class CreateRestaurantInteractor:
    def __init__(
        self,
        city_repository: city_repository.ICityRepository,
        restaurant_repository: restaurant_repository.IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ):
        self._city_repository = city_repository
        self._restaurant_repository = restaurant_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, city_id: int, restaurant_request: AddRestaurantRequest):
        if city_id < 1:
            raise IdNotValidError

        city = await self._city_repository.get_city_by_id(city_id)
        add_restaurant_response = await self._restaurant_repository.add_restaurant_to_city_by_id(
            city, restaurant_request
        )
        await self._transaction_manager.commit()

        return add_restaurant_response


class DeleteRestaurantInteractor:
    def __init__(
        self,
        restaurant_repository: restaurant_repository.IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ):
        self._restaurant_repository = restaurant_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, restaurant_id: int) -> DeleteRestaurantResponse:
        if restaurant_id < 1:
            raise IdNotValidError

        restaurant = await self._restaurant_repository.get_restaurant_by_id(restaurant_id)
        restaurant_response = await self._restaurant_repository.delete_restaurant(restaurant)
        await self._transaction_manager.commit()

        return restaurant_response
