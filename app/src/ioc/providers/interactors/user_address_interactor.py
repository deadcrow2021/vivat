from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.user_address_interactor import AddUserAddressInteractor, DeleteAddressInteractor, GetUserAddressInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.user_address_repository import IUserAddressRepository


class UserAddressInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_user_addresses_interactor(
        self,
        user_address_repository: IUserAddressRepository
    ) -> GetUserAddressInteractor:
        return GetUserAddressInteractor(user_address_repository)

    @provide(scope=Scope.REQUEST)
    async def add_user_address_interactor(
        self,
        user_address_repository: IUserAddressRepository,
        transaction_manager: ITransactionManager,
    ) -> AddUserAddressInteractor:
        return AddUserAddressInteractor(user_address_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    async def delete_user_address_interactor(
        self,
        user_address_repository: IUserAddressRepository,
        transaction_manager: ITransactionManager,
    ) -> DeleteAddressInteractor:
        return DeleteAddressInteractor(user_address_repository, transaction_manager)
