from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.order_interactor import AddOrderInteractor, GetUserOrdersInteractor#, UpdateOrderStatusInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.notification.notifier import INotifier
from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.application.interfaces.repositories.user_address_repository import IUserAddressRepository
from src.application.interfaces.repositories.users_repository import IUsersRepository


class OrderInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_orders_interactor(
        self,
        order_repository: IOrderRepository
    ) -> GetUserOrdersInteractor:
        return GetUserOrdersInteractor(order_repository)

    @provide(scope=Scope.REQUEST)
    async def add_order_interactor(
        self,
        order_repository: IOrderRepository,
        user_repository: IUsersRepository,
        user_address_repository: IUserAddressRepository,
        transaction_manager: ITransactionManager,
        notifier: INotifier,
    ) -> AddOrderInteractor:
        return AddOrderInteractor(
            order_repository,
            user_repository,
            user_address_repository,
            transaction_manager,
            notifier
        )
