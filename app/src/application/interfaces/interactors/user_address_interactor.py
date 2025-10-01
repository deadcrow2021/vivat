from sqlalchemy.exc import SQLAlchemyError

from src.domain.dto.user_address_dto import AddUserAddressRequest, AddUserAddressResponse, DeleteAddressResponse, GetUserAddress, UpdateUserAddressRequest, UpdateUserAddressResponse
from src.application.exceptions import DatabaseException, IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import user_address_repository


class GetUserAddressInteractor:
    def __init__(
        self, user_address_repository: user_address_repository.IUserAddressRepository,
    ):
        self._user_address_repository = user_address_repository

    async def __call__(self, user_id: int) -> GetUserAddress:
        if user_id < 1:
            raise IdNotValidError
        address_result = await self._user_address_repository.get_user_addresses_by_user_id(user_id)

        return [
            GetUserAddress(
                id=addr.id,
                address=addr.address,
                entrance=addr.entrance,
                floor=addr.floor,
                apartment=addr.apartment,
                is_primary=addr.is_primary
            )
            for addr in address_result
        ]


class AddUserAddressInteractor:
    def __init__(
        self,
        user_address_repository: user_address_repository.IUserAddressRepository,
        transaction_manager: ITransactionManager
    ):
        self._user_address_repository = user_address_repository
        self._transaction_manager = transaction_manager

    async def __call__(
        self,
        user_id: int,
        user_address_request: AddUserAddressRequest
    ) -> AddUserAddressResponse:
        if user_id < 1:
            raise IdNotValidError

        await self._user_address_repository.untag_user_addresses(user_id)
        address = await self._user_address_repository.add_address_to_user_by_id(user_id, user_address_request)
        await self._transaction_manager.commit()

        return AddUserAddressResponse(
            id=address.id,
            address=address.address,
            entrance=address.entrance,
            floor=address.floor,
            apartment=address.apartment,
            is_primary=address.is_primary
        )


class UpdateUserAddressInteractor:
    def __init__(
        self,
        user_address_repository: user_address_repository.IUserAddressRepository,
        transaction_manager: ITransactionManager
    ):
        self._user_address_repository = user_address_repository
        self._transaction_manager = transaction_manager

    async def __call__(
        self,
        address_id: int,
        user_id: int,
        address_request: UpdateUserAddressRequest
    ) -> UpdateUserAddressResponse:
        if address_id < 1 or user_id < 1:
            raise IdNotValidError

        if address_request.is_primary:
            await self._user_address_repository.untag_user_addresses(user_id)
        user_address = await self._user_address_repository.get_user_address_by_id(user_id, address_id)
        address = await self._user_address_repository.update_user_address(user_address, address_request)
        await self._transaction_manager.commit()

        return UpdateUserAddressResponse(
            id=address.id,
            address=address.address,
            entrance=address.entrance,
            floor=address.floor,
            apartment=address.apartment,
            is_primary=address.is_primary
        )


class DeleteAddressInteractor:
    def __init__(
        self,
        user_address_repository: user_address_repository.IUserAddressRepository,
        transaction_manager: ITransactionManager
    ):
        self._user_address_repository = user_address_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, user_id: int, address_id: int) -> DeleteAddressResponse:
        if address_id < 1 or user_id < 1:
            raise IdNotValidError

        address = await self._user_address_repository.delete_address(user_id, address_id)
        await self._transaction_manager.commit()

        return address
