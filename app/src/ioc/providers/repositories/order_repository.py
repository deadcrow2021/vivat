from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.infrastructure.adapters.repositories.order_repository import OrderRepository


class OrderRepositryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_order_repository(
        self, session: AsyncSession
    ) -> IOrderRepository:
        return OrderRepository(session)
