from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.order_dto import OrderResponse
from src.infrastructure.drivers.db.tables import Order


class IOrderRepository(Protocol):
    @abstractmethod
    async def create_order(self, order_request: OrderResponse) -> Order:
        raise NotImplementedError
