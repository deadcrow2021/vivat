from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.order_dto import OrderRequest
from src.application.interfaces.repositories.city_repository import ICityRepository
from src.infrastructure.drivers.db.tables import Order, User, Restaurant, UserAddress


class OrderRepository(ICityRepository): # TODO: add exceptions
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_order(self, order_request: OrderRequest) -> Order:
        user_query = select(User).filter(User.id == order_request.user_id)
        user_result = await self._session.execute(user_query)
        if not user_result.scalars().first():
            raise ValueError(f"User with id {order_request.user_id} not found") # TODO: add exceptions

        restaurant_query = select(Restaurant).filter(Restaurant.id == order_request.restaurant_id)
        restaurant_result = await self._session.execute(restaurant_query)
        if not restaurant_result.scalars().first():
            raise ValueError(f"Restaurant with id {order_request.restaurant_id} not found")

        address_query = select(UserAddress).filter(UserAddress.id == order_request.address_id)
        address_result = await self._session.execute(address_query)
        if not address_result.scalars().first():
            raise ValueError(f"Address with id {order_request.address_id} not found")
        
        new_order = Order(
            user_id=order_request.user_id,
            restaurant_id=order_request.restaurant_id,
            address_id=order_request.address_id,
            total_price=order_request.total_price,
            status=order_request.status
        )
        self._session.add(new_order)
        await self._session.flush()

        return new_order
