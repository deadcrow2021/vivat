from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.order_item_repository import IOrderItemRepository
from src.infrastructure.adapters.repositories.order_item_repository import OrderItemRepository


class OrderItemRepositryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_order_item_repository(
        self, session: AsyncSession
    ) -> IOrderItemRepository:
        return OrderItemRepository(session)
