from sqlalchemy.exc import SQLAlchemyError

from src.application.exceptions import DatabaseException
from src.infrastructure.drivers.db.tables import OrderItem
from src.domain.dto.order_item_dto import AddOrderItemRequest, AddOrderItemResponse
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import order_item_repository


class AddOrderItemInteractor:
    def __init__(
        self, order_item_repository: order_item_repository.IOrderItemRepository,
        transaction_manager: ITransactionManager
    ):
        self._order_item_repository = order_item_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, order_item_request: AddOrderItemRequest) -> AddOrderItemResponse:
        item: OrderItem = await self._order_item_repository.add_order_item_to_order_by_id(order_item_request)
        await self._transaction_manager.commit()

        return AddOrderItemResponse(
            id=item.id,
            food_id=item.food_variant_id,
            order_id=item.order_id,
            final_price=item.final_price
        )
