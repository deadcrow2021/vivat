from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.user_address_dto import AddUserAddressRequest
from src.application.interfaces.repositories.user_address_repository import IUserAddressRepository
from src.infrastructure.drivers.db.tables import UserAddress


class UserAddressRepository(IUserAddressRepository): # TODO: add exceptions
    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def add_address_to_user_by_id(
        self,
        user_id: int,
        user_address_request: AddUserAddressRequest
    ) -> UserAddress:
        new_address = UserAddress(
            user_id=user_id,
            address=user_address_request.address,
            entrance=user_address_request.entrance,
            floor=user_address_request.floor,
            apartment=user_address_request.apartment,
            is_primary=user_address_request.is_primary,
        )

        self._session.add(new_address)
        await self._session.flush()

        return new_address