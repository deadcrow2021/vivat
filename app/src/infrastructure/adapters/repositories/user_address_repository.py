from typing import List
from sqlalchemy import select, or_, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.user_address_dto import AddUserAddressRequest, DeleteAddressResponse
from src.application.interfaces.repositories.user_address_repository import IUserAddressRepository
from src.infrastructure.drivers.db.tables import UserAddress


class UserAddressRepository(IUserAddressRepository): # TODO: add exceptions
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def untag_user_addresses(self, user_id: int) -> None:
        address_query = (
            update(UserAddress)
            .filter(
                UserAddress.user_id == user_id,
                UserAddress.is_primary == True
            )
            .values(is_primary=False)
        )
        await self._session.execute(address_query)
        await self._session.flush()


    async def get_user_addresses_by_user_id(self, user_id: int) -> List[UserAddress]:
        stmt = select(UserAddress).where(UserAddress.user_id == user_id)
        address_result = await self._session.execute(stmt)
        address = address_result.scalars().all()

        return address


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
            is_primary=True,
        )

        self._session.add(new_address)
        await self._session.flush()

        return new_address

    # TODO: Update address

    async def delete_address(self, user_id: int, address_id: int) -> DeleteAddressResponse:
        stmt = select(UserAddress).filter(UserAddress.user_id == user_id, UserAddress.id == address_id)
        address_result = await self._session.execute(stmt)
        address = address_result.scalars().one_or_none()

        if not address:
            raise ValueError(f"User address with id {address_id} not found") # TODO: add exceptions

        await self._session.delete(address)
        await self._session.flush()

        await self._tag_address_as_primary(user_id, address)

        return DeleteAddressResponse(id=address.id)


    async def _tag_address_as_primary(self, user_id: int, deleted_address: UserAddress) -> None:
        if not deleted_address.is_primary:
            return

        stmt = select(UserAddress).where(UserAddress.user_id == user_id)
        address_result = await self._session.execute(stmt)
        address = address_result.scalars().first()
        if not address:
            return
        address.is_primary = True

        await self._session.flush()
