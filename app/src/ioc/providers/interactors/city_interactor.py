from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.city_interactor import GetCityInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.city_repository import (
    ICityRepository
)


class CityInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_city_interactor(
        self, city_repository: ICityRepository
    ) -> GetCityInteractor:
        return GetCityInteractor(city_repository)
