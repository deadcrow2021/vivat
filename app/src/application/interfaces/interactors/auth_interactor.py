from datetime import datetime, timezone

from fastapi import HTTPException, Request, Response
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from jose import JWTError, jwt

from src.infrastructure.exceptions import UserNotFoundError
from src.domain.dto.auth_dto import CreateUser, CreateUserResponse, CurrentUserDTO, LogOutResponse, LoginUserRequest, LoginUserResponse, LogInDTO, TokenResponse, UpdateUserResponse
from src.application.exceptions import DatabaseException, IdNotValidError, TokenError, UnhandledException
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import auth_repository, user_address_repository, restaurant_repository
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
        try:
            check_user = await self._auth_repository.get_user_by_phone(user_create_request.phone)
            if check_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Пользователь с таким номером уже зарегистрирован"
                )
            user = await self._auth_repository.register_user(user_create_request, self._config)
            await self._transaction_manager.commit()

            return CreateUserResponse(
                id=user.id,
                phone=user.phone # TODO: Могут зарегать не свой телефон. Проверять ip
            )
        except SQLAlchemyError:
            raise DatabaseException("Не удалось зарегистрировать пользователя в бд")


class LoginUserInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        user_address_repository: user_address_repository.IUserAddressRepository,
        restaurant_repository: restaurant_repository.IRestaurantRepository,
        transaction_manager: ITransactionManager,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._user_address_repository = user_address_repository
        self._restaurant_repository = restaurant_repository
        self._transaction_manager = transaction_manager
        self._config = config

    async def __call__(
        self,
        login_user_request: LoginUserRequest,
        response: Response
        ) -> LoginUserResponse:
        try:
            # TODO: Присылает что refresh токен не найден. Надо присылать Пользователь не зарегистрирован
            login_dto = await self._auth_repository.login_user(login_user_request, self._config)
            user_dto = login_dto.user
            
            user_adress = await self._user_address_repository.get_primary_or_latest_address(user_dto.user_id)
            restaurant_address = await self._restaurant_repository.get_restaurant_by_last_user_order(user_dto.user_id)
            await self._transaction_manager.commit()

            # Access Token
            response.set_cookie(
                key=self._config.token.access_token_cookie_key,
                value=login_dto.access_token,
                httponly=True, # HttpOnly Cookie
                max_age=self._config.token.access_token_expire_minutes * 60,
                secure=_is_secure(self._config),
                samesite="Lax"
            )
            # Refresh Token
            response.set_cookie(
                key=self._config.token.refresh_token_cookie_key,
                value=login_dto.refresh_token,
                httponly=True, # HttpOnly Cookie
                max_age=self._config.token.refresh_token_expire_days * 24 * 3600,
                secure=_is_secure(self._config),
                samesite="Lax"
            )

            return LoginUserResponse(
                id=login_dto.user.user_id,
                phone=login_dto.user.phone,
                order_user_address_id=user_adress.id if user_adress else None,
                order_restaurant_address_id=restaurant_address.id if restaurant_address else None
            )

        except SQLAlchemyError:
            raise DatabaseException("Не удалось войти в систему в бд")


class UpdateAccessTokenInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._config = config

    async def __call__(self, request: Request, response: Response) -> TokenResponse:
        try:
            token_config = self._config.token
            refresh_token = request.cookies.get(self._config.token.refresh_token_cookie_key)

            if not refresh_token:
                raise TokenError("Refresh токен не найден")

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
                    raise TokenError("Невалидный токен. Не удалось получить номер телефона из токена")
                if not expires:
                    raise TokenError("Невалидный токен. Не удалось получить время жизни токена")
                if expires < datetime.now(timezone.utc).timestamp():
                    raise TokenError("Невалидный токен. Токен просрочен")
            except JWTError:
                raise TokenError("Невалидный токен")
            except Exception as e:
                raise TokenError(f'Неизвестная ошибка токена: {str(e)}')

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

        except SQLAlchemyError:
            raise DatabaseException("Не удалось обновить токен в бд")


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

    async def __call__(self, request: Request, response: Response) -> LogOutResponse:
        try:
            tokens_revoked = 0
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
                    await self._transaction_manager.commit()

                except JWTError:
                    raise TokenError("Невалидный токен")
                except Exception as e:
                    raise TokenError(f'Неизвестная ошибка токена: {str(e)}')

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
            return LogOutResponse(
                message="Logout success",
                tokens_revoked=tokens_revoked
            )

        except SQLAlchemyError:
            raise DatabaseException("Не удалось выйти из системы в бд")


class GetCurrentUserInteractor:
    def __init__(
        self,
        auth_repository: auth_repository.IAuthRepository,
        config: Config
    ):
        self._auth_repository = auth_repository
        self._config = config

    async def __call__(self, request: Request) -> CurrentUserDTO:
        try:
            token_config = self._config.token

            access_token = request.cookies.get(token_config.access_token_cookie_key)
            if not access_token:
                raise TokenError("Информация о пользователе не найдена. Необходимо войти в систему") # Access токен не найден

            try:
                # Декодируем токен
                payload = jwt.decode(
                    access_token,
                    token_config.secret_key,
                    algorithms=[token_config.algorithm]
                )
                phone: str = payload.get("sub")
                if not phone:
                    raise TokenError("Невалидный токен. Не удалось получить номер телефона из токена")

            except JWTError:
                raise TokenError("Невалидный токен")

            # Получаем пользователя из репозитория
            user = await self._auth_repository.get_user_by_phone(phone)
            if not user:
                raise UserNotFoundError

            return CurrentUserDTO(
                id=user.id,
                phone=user.phone.e164
            )

        except SQLAlchemyError:
            raise DatabaseException("Не удалось получить пользователя из токена в базы данных")


def _is_secure(config: Config):
    '''Только для HTTPS в production'''
    if config.app.environment == 'production':
        return True
    return False
