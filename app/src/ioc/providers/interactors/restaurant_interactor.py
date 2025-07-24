from dishka import provide, Provider, Scope

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.interactors.restaurant_interactor import (
    ChangeRestaurantInteractor,
    DeleteRestaurantInteractor,
    GetRestaurantInteractor,
    CreateRestaurantInteractor,
)
from src.application.interfaces.repositories.restaurant_repository import (
    IRestaurantRepository,
)


class RestaurantInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_restaurant_interactor(
        self, restaurant_repository: IRestaurantRepository
    ) -> GetRestaurantInteractor:
        return GetRestaurantInteractor(restaurant_repository)

    @provide(scope=Scope.REQUEST)
    async def create_restaurant_interactor(
        self,
        restaurant_repository: IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ) -> CreateRestaurantInteractor:
        return CreateRestaurantInteractor(restaurant_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    async def change_restaurant_interactor(
        self,
        restaurant_repository: IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ) -> ChangeRestaurantInteractor:
        return ChangeRestaurantInteractor(restaurant_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    async def delete_restaurant_interactor(
        self,
        restaurant_repository: IRestaurantRepository,
        transaction_manager: ITransactionManager,
    ) -> DeleteRestaurantInteractor:
        return DeleteRestaurantInteractor(restaurant_repository, transaction_manager)
