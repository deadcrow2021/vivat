from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.users_interactor import GetUserInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.users_repository import IUsersRepository
from src.config import Config


class UsersInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_user_interactor(
        self,
        users_repository: IUsersRepository,
        transaction_manager: ITransactionManager,
    ) -> GetUserInteractor:
        return GetUserInteractor(users_repository, transaction_manager)
