from dishka import provide, Provider, Scope

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.interactors.food_variant_interactor import GetFoodVariantInteractor
from src.application.interfaces.repositories.food_variant_repository import IFoodVariantRepository


class FoodVariantInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_food_variant_interactor(
        self,
        food_variant_repository: IFoodVariantRepository
    ) -> GetFoodVariantInteractor:
        return GetFoodVariantInteractor(food_variant_repository)
