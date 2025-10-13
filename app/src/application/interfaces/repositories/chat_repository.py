from abc import abstractmethod
from typing import List, Optional, Protocol

from src.infrastructure.drivers.db.tables import TelegramChat


class IChatRepository(Protocol):
    @abstractmethod
    async def get_chat(self, chat_id: int) -> Optional[TelegramChat]:
        raise NotImplementedError
