from datetime import datetime, timezone

from fastapi import HTTPException, Request, Response
from starlette import status
from jose import JWTError, jwt

from src.domain.dto.auth_dto import CreateUser, CreateUserResponse, CurrentUserDTO, LogOutResponse, LoginUserRequest, LoginUserResponse, LogInDTO, TokenResponse, UpdateUserResponse
from src.application.exceptions import IdNotValidError, TokenError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import auth_repository
from src.config import Config
from src.logger import logger


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
            # email=user.email,
            phone=user.phone # TODO: Могут зарегать не свой телефон
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

    async def __call__(self, login_user_request: LoginUserRequest, response: Response) -> LoginUserResponse:
        user_dto = await self._auth_repository.login_user(login_user_request, self._config)
        await self._transaction_manager.commit()

        # Access Token
        response.set_cookie(
            key=self._config.token.access_token_cookie_key,
            value=user_dto.access_token,
            httponly=True, # HttpOnly Cookie
            max_age=self._config.token.access_token_expire_minutes * 60,
            secure=_is_secure(self._config),
            samesite="Lax"
        )
        # Refresh Token
        response.set_cookie(
            key=self._config.token.refresh_token_cookie_key,
            value=user_dto.refresh_token,
            httponly=True, # HttpOnly Cookie
            max_age=self._config.token.refresh_token_expire_days * 24 * 3600,
            secure=_is_secure(self._config),
            samesite="Lax"
        )

        return LoginUserResponse(
            id=user_dto.user.user_id,
            phone=user_dto.user.phone
        )


class UpdateAccessTokenInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._config = config

    async def __call__(self, request: Request, response: Response) -> TokenResponse:
        token_config = self._config.token

        refresh_token = request.cookies.get(self._config.token.refresh_token_cookie_key)
        if not refresh_token:
            raise TokenError("Refresh token missing")

        try:
            # {'sub': '+79111111111', 'exp': 1758720000}
            payload = jwt.decode(
                refresh_token,
                token_config.secret_key,
                algorithms=[token_config.algorithm]
            )
            user_phone: str = payload.get("sub")
            expires: int = payload.get("exp")
            if not user_phone:
                raise TokenError("Invalid token. Can\'t get phone from token")
            if not expires:
                raise TokenError("Invalid token. Can\'t get phone from token")
            if expires < datetime.now(timezone.utc).timestamp():
                raise TokenError("Invalid token. Token expired")
        except JWTError:
            raise TokenError("Invalid token")
        except Exception as e:
            raise TokenError(f'Unknown token error: {str(e)}')

        user_dto: LogInDTO = await self._auth_repository.update_access_token(user_phone, refresh_token, self._config)

        # Access Token
        response.set_cookie(
            key=self._config.token.access_token_cookie_key,
            value=user_dto.access_token,
            httponly=True, # HttpOnly Cookie
            max_age=self._config.token.access_token_expire_minutes * 60,
            secure=_is_secure(self._config),
            samesite="Lax"
        )
        # Генерация нового access токена
        return UpdateUserResponse(
            id=user_dto.user.user_id,
            phone=user_dto.user.phone
        )


class LogoutInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        transaction_manager: ITransactionManager,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._transaction_manager = transaction_manager
        self._config = config

    async def __call__(self, request: Request, response: Response) -> TokenResponse:
        token_config = self._config.token

        refresh_token = request.cookies.get(self._config.token.refresh_token_cookie_key)
        if refresh_token:
            try:
                payload = jwt.decode(
                    refresh_token,
                    token_config.secret_key,
                    algorithms=[token_config.algorithm]
                )
                user_phone: str = payload.get("sub")
                if user_phone:
                    tokens_revoked = await self._auth_repository.revoke_all_user_refresh_tokens(user_phone)
            except JWTError:
                logger.warning("Invalid token")

        await self._transaction_manager.commit()
        
        response.delete_cookie(
            key=self._config.token.access_token_cookie_key,
            httponly=True,
            secure=_is_secure(self._config),
            samesite="Lax"
        )
        response.delete_cookie(
            key=self._config.token.refresh_token_cookie_key,
            httponly=True,
            secure=_is_secure(self._config),
            samesite="Lax"
        )

        return LogOutResponse(tokens_revoked=tokens_revoked)


class GetCurrentUserInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._config = config

    async def __call__(self, request: Request) -> CurrentUserDTO:
        token_config = self._config.token
        
        # Получаем токен из cookies
        access_token = request.cookies.get(token_config.access_token_cookie_key)
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        try:
            # Декодируем токен
            payload = jwt.decode(
                access_token,
                token_config.secret_key,
                algorithms=[token_config.algorithm]
            )
            phone: str = payload.get("sub")
            if not phone:
                raise TokenError("Invalid token. Can't get phone from token")
                
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Получаем пользователя из репозитория
        user = await self._auth_repository.get_user_by_phone(phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return CurrentUserDTO(
            id=user.id,
            phone=user.phone.e164
        )


def _is_secure(config: Config):
    '''Только для HTTPS в production'''
    if config.app.environment == 'production':
        return True
    return False
