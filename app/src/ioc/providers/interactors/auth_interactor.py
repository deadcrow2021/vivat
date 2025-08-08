from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.auth_interactor import LoginUserInteractor, RegisterUserInteractor, UpdateAccessTokenInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.auth_repository import IAuthRepository
from src.config import Config


class AuthInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def register_user_interactor(
        self,
        auth_repository: IAuthRepository,
        transaction_manager: ITransactionManager,
        config: Config
    ) -> RegisterUserInteractor:
        return RegisterUserInteractor(auth_repository, transaction_manager, config)

    @provide(scope=Scope.REQUEST)
    async def login_user_interactor(
        self,
        auth_repository: IAuthRepository,
        transaction_manager: ITransactionManager,
        config: Config
    ) -> LoginUserInteractor:
        return LoginUserInteractor(auth_repository, transaction_manager, config)

    @provide(scope=Scope.REQUEST)
    async def login_interactor(
        self,
        auth_repository: IAuthRepository,
        transaction_manager: ITransactionManager,
        config: Config
    ) -> LoginUserInteractor:
        return LoginUserInteractor(auth_repository, transaction_manager, config)

    @provide(scope=Scope.REQUEST)
    async def update_token_interactor(
        self,
        auth_repository: IAuthRepository,
        config: Config
    ) -> UpdateAccessTokenInteractor:
        return UpdateAccessTokenInteractor(auth_repository, config)
