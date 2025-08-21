from dishka import provide, Provider, Scope

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.interactors.food_interactor import AddFoodInteractor, GetFoodInteractor
from src.application.interfaces.repositories.food_repository import IFoodRepository


class FoodInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_food_interactor(
        self, food_repository: IFoodRepository
    ) -> GetFoodInteractor:
        return GetFoodInteractor(food_repository)

    @provide(scope=Scope.REQUEST)
    async def add_food_interactor(
        self,
        food_repository: IFoodRepository,
        transaction_manager: ITransactionManager,
    ) -> AddFoodInteractor:
        return AddFoodInteractor(food_repository, transaction_manager)
