from typing import List, Optional
from sqlalchemy import select, or_, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import UserAddressNotFoundError
from src.domain.dto.user_address_dto import AddUserAddressRequest, DeleteAddressResponse, UpdateUserAddressRequest
from src.application.interfaces.repositories.user_address_repository import IUserAddressRepository
from src.infrastructure.drivers.db.tables import UserAddress


class UserAddressRepository(IUserAddressRepository):
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


    async def tag_user_address(self, user_id: int, address_id: int) -> None:
        address_query = (
            update(UserAddress)
            .filter(
                UserAddress.user_id == user_id,
                UserAddress.id == address_id,
            )
            .values(is_primary=True)
        )
        await self._session.execute(address_query)
        await self._session.flush()


    async def get_user_address_by_id(self, user_id: int, address_id: int) -> UserAddress:
        stmt = (
            select(UserAddress)
            .where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id
            )
        )
        address_result = await self._session.execute(stmt)
        address = address_result.scalars().first()
        
        if not address:
            raise UserAddressNotFoundError(id=address_id)

        return address


    async def get_user_addresses_by_user_id(self, user_id: int) -> List[UserAddress]:
        stmt = select(UserAddress).where(UserAddress.user_id == user_id)
        address_result = await self._session.execute(stmt)
        address = address_result.scalars().all()

        return address


    async def get_primary_or_latest_address(self, user_id: int) -> Optional[UserAddress]:
        stmt = (
            select(UserAddress)
            .filter(
                UserAddress.user_id == user_id,
                UserAddress.is_removed == False
            )
            .order_by(
                UserAddress.is_primary.desc(),  # Primary addresses first
                UserAddress.id.desc()           # Latest address if no primary
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()


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


    async def update_user_address(
        self,
        user_address: UserAddress,
        address_request: UpdateUserAddressRequest
    ) -> UserAddress:
        update_dict = address_request.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user_address, key, value)

        await self._session.flush()
        return user_address


    async def delete_address(self, user_id: int, address_id: int) -> DeleteAddressResponse:
        stmt = select(UserAddress).filter(UserAddress.user_id == user_id, UserAddress.id == address_id)
        address_result = await self._session.execute(stmt)
        address = address_result.scalars().one_or_none()

        if not address:
            raise UserAddressNotFoundError(id=address_id)

        if address.is_primary:
            new_address_stmt = (
                select(UserAddress)
                .filter(UserAddress.user_id == user_id, UserAddress.id != address.id)
                .order_by(UserAddress.id.desc())
                .limit(1)
            )
            new_result = await self._session.execute(new_address_stmt)
            new_address = new_result.scalars().first()

            if new_address:
                new_address.is_primary = True
                await self._session.flush()

        await self._session.delete(address)
        await self._session.flush()

        return DeleteAddressResponse(id=address.id)
