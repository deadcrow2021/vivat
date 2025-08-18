from src.domain.dto.order_dto import OrderRequest, OrderResponse
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import order_repository


# TODO: add exceptions
class AddOrderInteractor:
    def __init__(
        self,
        order_repository: order_repository.IOrderRepository,
        transaction_manager: ITransactionManager
    ):
        self._order_repository = order_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, order_request: OrderRequest) -> OrderResponse:
        order = await self._order_repository.create_order(order_request)
        await self._transaction_manager.commit()

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            restaurant_id=order.restaurant_id,
            address_id=order.address_id,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
