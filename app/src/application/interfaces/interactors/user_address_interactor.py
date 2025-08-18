from src.domain.dto.user_address_dto import AddUserAddressRequest, AddUserAddressResponse
from src.application.exceptions import IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import user_address_repository


# TODO: add exceptions
class AddUserAddressInteractor:
    def __init__(
        self, user_address_repository: user_address_repository.IUserAddressRepository,
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

        address = await self._user_address_repository.add_address_to_user_by_id(user_id, user_address_request)
        await self._transaction_manager.commit()

        return AddUserAddressResponse(
            address=address.address,
            entrance=address.entrance,
            floor=address.floor,
            apartment=address.apartment,
            is_primary=address.is_primary
        )
