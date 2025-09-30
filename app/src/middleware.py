import traceback

from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Request, Response

from src.config import Config, create_config
from src.logger import logger


async def exception_middleware(request: Request, call_next) -> Response:
    config: Config = create_config()
    environment = config.app.environment

    try:
        logger.debug(f"start request")
        response = await call_next(request)
        logger.debug(f"end request")
        return response

    except SQLAlchemyError as exc:
        # Логируем ошибки БД, которые не были обработаны в интеракторах
        logger.error(f"Log Database error: --> {str(exc)} <--")
        logger.debug(f"Log Database error traceback: --> {traceback.format_exc()} <--")
        if environment == "development":
            return JSONResponse(
                status_code=500,
                content={
                    "detail": f"Database error: {str(exc)}",
                    "traceback": traceback.format_exc()
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Database operation failed"
                }
            )

    except Exception as exc:
        # Логируем все остальные неперехваченные исключения
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        
        if environment == "development":
            return JSONResponse(
                status_code=500,
                content={
                    "detail": f"Unhandled error: {str(exc)}",
                    "traceback": traceback.format_exc()
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
