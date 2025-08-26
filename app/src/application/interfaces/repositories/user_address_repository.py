from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.user_address_dto import AddUserAddressRequest, DeleteAddressResponse
from src.infrastructure.drivers.db.tables import UserAddress


class IUserAddressRepository(Protocol):
    @abstractmethod
    async def untag_user_addresses(self, user_id: int) -> None: 
        raise NotImplementedError

    @abstractmethod
    async def get_user_addresses_by_user_id(self, user_id: int) -> List[UserAddress]:
        raise NotImplementedError

    @abstractmethod
    async def add_address_to_user_by_id(
        self,
        user_id: int,
        user_address_request: AddUserAddressRequest
    ) -> UserAddress:
        raise NotImplementedError

    @abstractmethod
    async def delete_address(self, user_id: int, address_id: int) -> DeleteAddressResponse:
        raise NotImplementedError
