from dishka import provide, Provider, Scope

from src.application.interfaces.repositories.city_repository import ICityRepository
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.interactors.restaurant_interactor import (
    UpdateRestaurantInteractor,
    DeleteRestaurantInteractor,
    GetCityRestaurantsInteractor,
    CreateRestaurantInteractor,
    GetRestaurantInteractor,
)
from src.application.interfaces.repositories.restaurant_repository import (
    IRestaurantRepository,
)


class RestaurantInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_restaurant_interactor(
        self,
        restaurant_repository: IRestaurantRepository,
    ) -> GetRestaurantInteractor:
        return GetRestaurantInteractor(restaurant_repository)

    @provide(scope=Scope.REQUEST)
    async def get_city_restaurants_interactor(
        self,
        city_repository: ICityRepository,
        restaurant_repository: IRestaurantRepository,
    ) -> GetCityRestaurantsInteractor:
        return GetCityRestaurantsInteractor(city_repository, restaurant_repository)

    @provide(scope=Scope.REQUEST)
    async def update_restaurant_interactor(
        self,
        restaurant_repository: IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ) -> UpdateRestaurantInteractor:
        return UpdateRestaurantInteractor(restaurant_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    async def create_restaurant_interactor(
        self,
        city_repository: ICityRepository,
        restaurant_repository: IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ) -> CreateRestaurantInteractor:
        return CreateRestaurantInteractor(city_repository, restaurant_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    async def delete_restaurant_interactor(
        self,
        restaurant_repository: IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ) -> DeleteRestaurantInteractor:
        return DeleteRestaurantInteractor(restaurant_repository, transaction_manager)
