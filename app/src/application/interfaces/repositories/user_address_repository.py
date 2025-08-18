from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.user_address_dto import AddUserAddressRequest
from src.infrastructure.drivers.db.tables import UserAddress


class IUserAddressRepository(Protocol):
    @abstractmethod
    async def add_address_to_user_by_id(
        self,
        user_id: int,
        user_address_request: AddUserAddressRequest
    ) -> UserAddress:
        raise NotImplementedError
