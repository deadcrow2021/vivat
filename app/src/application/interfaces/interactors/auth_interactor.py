from fastapi import Request, Response
from jose import JWTError, jwt

from src.domain.dto.auth_dto import CreateUser, CreateUserResponse, LoginUserRequest, TokenDTO, TokenResponse
from src.application.exceptions import IdNotValidError, TokenError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import auth_repository
from src.config import Config


class RegisterUserInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        transaction_manager: ITransactionManager,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._transaction_manager = transaction_manager
        self._config = config

    async def __call__(self, user_create_request: CreateUser) -> CreateUserResponse:
        user = await self._auth_repository.register_user(user_create_request, self._config)

        await self._transaction_manager.commit()

        return CreateUserResponse(
            id=user.id,
            email=user.email,
            phone=user.phone
        )


class LoginUserInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        transaction_manager: ITransactionManager,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._transaction_manager = transaction_manager
        self._config = config

    async def __call__(self, login_user_request: LoginUserRequest, response: Response) -> TokenDTO:
        user_token = await self._auth_repository.login_user(login_user_request, self._config)

        response.set_cookie(
            key=self._config.token.refresh_token_cookie_key,
            value=user_token.refresh_token,
            httponly=True, # HttpOnly Cookie
            max_age=self._config.token.refresh_token_expire_days * 24 * 3600,
            secure=True if self._config.app.environment == 'production' else False, # Только для HTTPS в production
            samesite="Lax"
        )

        return TokenResponse(
            access_token=user_token.access_token,
            token_type=user_token.token_type
        )

class UpdateAccessTokenInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._config = config

    async def __call__(self, request: Request) -> TokenResponse:
        token_config = self._config.token
        refresh_token = request.cookies.get(self._config.token.refresh_token_cookie_key)
        if not refresh_token:
            raise TokenError("Refresh token missing")

        try:
            payload = jwt.decode(refresh_token, token_config.secret_key, algorithms=[token_config.algorithm])
            user_phone: str = payload.get("sub")
            if not user_phone:
                raise TokenError("Invalid token. Can\'t get phone from token")
        except JWTError:
            raise TokenError("Invalid token")

        # Проверка существования пользователя
        user_token: TokenDTO = await self._auth_repository.update_access_token(user_phone)

        # Генерация нового access токена
        return TokenResponse(access_token=user_token.access_token, token_type=user_token.token_type)
