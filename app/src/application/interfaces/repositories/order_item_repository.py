from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.order_item_dto import AddOrderItemRequest
from src.infrastructure.drivers.db.tables import OrderItem


class IOrderItemRepository(Protocol):
    @abstractmethod
    async def add_order_item_to_order_by_id(self, order_id: int, order_request: AddOrderItemRequest) -> OrderItem:
        raise NotImplementedError
