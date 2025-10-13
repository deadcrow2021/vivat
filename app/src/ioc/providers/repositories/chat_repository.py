from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.chat_repository import IChatRepository
from src.infrastructure.adapters.telegram.chat_repository import ChatRepository


class ChatRepositryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_chat_repository(
        self,
        session: AsyncSession
    ) -> IChatRepository:
        return ChatRepository(session)
