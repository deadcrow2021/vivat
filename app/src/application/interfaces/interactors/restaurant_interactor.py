from src.application.exceptions import IdNotValidError
from src.domain.dto.restaurant_dto import (
    AddRestaurantRequest,
    DeleteRestaurantResponse,
    GetRestaurantsResponse,
    UpdateRestaurantRequest,
)
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import restaurant_repository


class GetRestaurantInteractor:
    def __init__(
        self, restaurant_repository: restaurant_repository.IRestaurantRepository
    ):
        self._restaurant_repository = restaurant_repository

    async def __call__(self, city_id: int) -> GetRestaurantsResponse:
        if city_id < 1:
            raise IdNotValidError

        city: GetRestaurantsResponse = (
            await self._restaurant_repository.get_restaurants_by_city_id(city_id)
        )

        return city


class CreateRestaurantInteractor:
    def __init__(
        self,
        restaurant_repository: restaurant_repository.IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ):
        self._restaurant_repository = restaurant_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, city_id: int, restaurant: AddRestaurantRequest):
        if city_id < 1:
            raise IdNotValidError

        city = await self._restaurant_repository.add_restaurant_to_city_by_id(
            city_id, restaurant
        )
        await self._transaction_manager.commit()

        return city


class ChangeRestaurantInteractor:
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
        restaurant: UpdateRestaurantRequest,
    ) -> None:
        if restaurant_id < 1:
            raise IdNotValidError

        restaurant = await self._restaurant_repository.change_restaurant_by_id(
            restaurant_id, restaurant
        )
        await self._transaction_manager.commit()

        return restaurant


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

        restaurant = await self._restaurant_repository.delete_restaurant_by_id(
            restaurant_id
        )
        await self._transaction_manager.commit()

        return restaurant
