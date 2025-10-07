from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.order_interactor import AddOrderInteractor#, UpdateOrderStatusInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.notification.notifier import IOrderNotifier
from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.application.interfaces.repositories.user_address_repository import IUserAddressRepository


class OrderInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def add_order_interactor(
        self,
        order_repository: IOrderRepository,
        user_address_repository: IUserAddressRepository,
        transaction_manager: ITransactionManager,
        notifier: IOrderNotifier,
    ) -> AddOrderInteractor:
        return AddOrderInteractor(order_repository, user_address_repository, transaction_manager, notifier)

    # @provide(scope=Scope.REQUEST)
    # async def update_order_status_interactor(
    #     self,
    #     order_repository: IOrderRepository,
    #     transaction_manager: ITransactionManager,
    # ) -> UpdateOrderStatusInteractor:
    #     return UpdateOrderStatusInteractor(order_repository, transaction_manager)
