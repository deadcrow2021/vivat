from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.city_interactor import AddCityInteractor, DeleteCityInteractor, GetAllCitiesInteractor, GetCityInteractor, UpdateCityInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.city_repository import ICityRepository


class CityInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_cities_interactor(
        self, city_repository: ICityRepository
    ) -> GetAllCitiesInteractor:
        return GetAllCitiesInteractor(city_repository)

    @provide(scope=Scope.REQUEST)
    async def get_city_interactor(
        self, city_repository: ICityRepository
    ) -> GetCityInteractor:
        return GetCityInteractor(city_repository)

    @provide(scope=Scope.REQUEST)
    async def add_city_interactor(
        self,
        city_repository: ICityRepository,
        transaction_manager: ITransactionManager,
    ) -> AddCityInteractor:
        return AddCityInteractor(city_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    async def update_city_interactor(
        self,
        city_repository: ICityRepository,
        transaction_manager: ITransactionManager,
    ) -> UpdateCityInteractor:
        return UpdateCityInteractor(city_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    async def delete_city_interactor(
        self,
        city_repository: ICityRepository,
        transaction_manager: ITransactionManager,
    ) -> DeleteCityInteractor:
        return DeleteCityInteractor(city_repository, transaction_manager)
