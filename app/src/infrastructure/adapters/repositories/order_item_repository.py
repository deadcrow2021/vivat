from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.order_item_dto import AddOrderItemRequest
from src.application.interfaces.repositories.order_item_repository import IOrderItemRepository
from src.infrastructure.drivers.db.tables import Food, Order, OrderItem


class OrderItemRepository(IOrderItemRepository): # TODO: add exceptions
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_order_item_to_order_by_id(self, order_request: AddOrderItemRequest) -> OrderItem:
        food_query = select(Food).filter(Food.id == order_request.food_id)
        query_result = await self._session.execute(food_query)
        if not query_result.scalars().first():
            raise ValueError(f"Food with id {order_request.order_id} not found") # TODO: add exceptions

        order_query = select(Order).filter(Order.id == order_request.order_id)
        query_result = await self._session.execute(order_query)
        if not query_result.scalars().first():
            raise ValueError(f"Order with id {order_request.order_id} not found") # TODO: add exceptions

        new_order_item = OrderItem(
            food_id=order_request.food_id,
            order_id=order_request.order_id,
            final_price=order_request.final_price
        )

        self._session.add(new_order_item)
        await self._session.flush()

        return new_order_item
