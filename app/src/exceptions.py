from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from src.application import exceptions as app_exc
from src.domain import exceptions as domain_exc
from src.infrastructure import exceptions as infra_exc


def register_exception_handlers(app: FastAPI) -> None:
    # FASTAPI EXCEPTION HANDLERS

    # Обработчик для ошибок валидации Pydantic (RequestValidationError)
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            # field = "->".join(str(loc) for loc in error["loc"])  # "body->name", "query->latitude" и т.д.
            errors.append({
                "field": error["loc"][1],
                "message": error["msg"],
                "type": error["type"],
            })
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,  # или 400, если предпочитаете
            content={
                "detail": "Validation error",
                "errors": errors,
            },
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

    # APPLICATION EXCEPTION HANDLERS

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
