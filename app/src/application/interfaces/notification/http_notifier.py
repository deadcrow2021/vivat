from abc import abstractmethod
from typing import Protocol

from src.domain.enums.enums import OrderAction


class IHTTPOrderNotifier(Protocol):
    @abstractmethod
    async def send_order_info_to_bot(
        self,
        restaurant_id: int,
        order_id: int,
        message_text: str,
        current_status: str,
        action: OrderAction
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_order_message(
        self,
        chat_id: int,
        message_id: int,
        order_id: int,
        message_text: str,
        current_status: str,
        action: OrderAction
    ) -> None:
        raise NotImplementedError
