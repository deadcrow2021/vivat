from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from src.application import exceptions as app_exc
from src.domain import exceptions as domain_exc
from src.infrastructure import exceptions as infra_exc


def register_exception_handlers(app: FastAPI) -> None:
    # FASTAPI EXCEPTION HANDLERS
    
    @app.exception_handler(ValueError)
    async def value_exception_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    @app.exception_handler(app_exc.UnhandledException)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f'Неизвестная ошибка: {exc}'},
        )

    # INFRASTRUCTURE EXCEPTION HANDLERS
    @app.exception_handler(infra_exc.InvalidCredentialsError)
    async def invalid_credentials_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(infra_exc.CityNotFoundError)
    async def city_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.RestaurantNotFoundError)
    async def restaurant_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.FeatureNotFoundError)
    async def feature_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.FoodNotFoundError)
    async def food_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.IngredientsNotFoundError)
    async def ingredients_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.MenuCategoryNotFoundError)
    async def menu_category_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.UserNotFoundError)
    async def user_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.UserExistsError)
    async def user_exists_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.VariantNotFoundError)
    async def variant_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(infra_exc.UserAddressNotFoundError)
    async def user_address_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    # APPLICATION EXCEPTION HANDLERS

    @app.exception_handler(app_exc.DatabaseException)
    async def database_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    @app.exception_handler(app_exc.IdNotValidError)
    async def id_not_valid_handler(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Id is not valid."},
        )

    @app.exception_handler(app_exc.TokenError)
    async def token_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    # DOMAIN EXCEPTION HANDLERS

    # Обработчик для ошибок валидации Pydantic (RequestValidationError)
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        messages = []
        
        if isinstance(errors, str):
            messages = [errors]
        else:
            for err in errors:
                field = ' - '.join(str(field) for field in err.get('loc'))
                err_msg = err.get('msg')
                msg = f'{err_msg} - {field}'
                messages.append(msg)
    
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": ' | '.join(messages)},
        )