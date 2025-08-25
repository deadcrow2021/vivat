from src.domain.dto.user_address_dto import AddUserAddressRequest, AddUserAddressResponse
from src.application.exceptions import IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import user_address_repository


# TODO: add exceptions
# class GetUserAddressInteractor:
#     def __init__(
#         self, user_address_repository: user_address_repository.IUserAddressRepository,
#     ):
#         self._user_address_repository = user_address_repository

#     async def __call__(self, city_id: int) -> GetCityResponse:
#         if city_id < 1:
#             raise IdNotValidError

#         city = await self._city_repository.get_city_by_id(city_id)
        
#         return 


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
