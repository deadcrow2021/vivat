from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.order_item_interactor import AddOrderItemInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.order_item_repository import IOrderItemRepository


class OrderItemInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def add_order_item_interactor(
        self,
        order_item_repository: IOrderItemRepository,
        transaction_manager: ITransactionManager,
    ) -> AddOrderItemInteractor:
        return AddOrderItemInteractor(order_item_repository, transaction_manager)