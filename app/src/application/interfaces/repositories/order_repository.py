from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.order_dto import OrderRequest, CreateOrderResponse, OrderStatus
from src.infrastructure.drivers.db.tables import Order


class IOrderRepository(Protocol):
    @abstractmethod
    async def create_order(
        self,
        order_request: OrderRequest,
        user_id: int
    ) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus
    ) -> Order:
        raise NotImplementedError
