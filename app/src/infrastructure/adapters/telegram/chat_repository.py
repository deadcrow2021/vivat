from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.chat_repository import IChatRepository
from src.infrastructure.drivers.db.tables import TelegramChat


class ChatRepository(IChatRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_chat(self, chat_id: str) -> Optional[TelegramChat]:
        stmt = (
            select(TelegramChat)
            .where(
                TelegramChat.chat_id == chat_id
            )
        )
        chat_result = await self._session.execute(stmt)
        chat = chat_result.scalars().first()
        return chat
