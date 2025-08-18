from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.order_interactor import AddOrderInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.order_repository import IOrderRepository


class OrderInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def add_city_interactor(
        self,
        order_repository: IOrderRepository,
        transaction_manager: ITransactionManager,
    ) -> AddOrderInteractor:
        return AddOrderInteractor(order_repository, transaction_manager)