from dishka import provide, Provider, Scope

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.interactors.food_characteristic_interactor import AddCharacteristicsToVariantInteractor
from src.application.interfaces.repositories.food_characteristic_repository import IFoodCharacteristicRepository


class FoodCharacteristicInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_characteristic_interactor(
        self,
        food_characteristic_repository: IFoodCharacteristicRepository,
        transaction_manager: ITransactionManager,
    ) -> AddCharacteristicsToVariantInteractor:
        return AddCharacteristicsToVariantInteractor(food_characteristic_repository, transaction_manager)
