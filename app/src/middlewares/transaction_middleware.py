import traceback

from dishka import AsyncContainer, FromDishka
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Request, Response

from src.application.interfaces.transaction_manager import ITransactionManager
from src.config import Config, create_config
from src.ioc.ioc_main import create_container
from src.logger import logger


def _get_isolation_level_for_request(request: Request) -> str:
    # path = request.url.path
    method = request.method

    # Клиент может запросить уровень изоляции через заголовок
    # isolation_header = request.headers.get("X-Transaction-Isolation")
    # if isolation_header in ["READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"]:
    #     return isolation_header
    
    # Критичные операции - строгая изоляция
    # if any(op in path for op in ['/payment', '/transfer', '/balance']):
    #     return "REPEATABLE READ"
    
    # Операции изменения данных - средняя изоляция  
    if method in ["POST", "PUT", "PATCH", "DELETE"]:
        return "REPEATABLE READ"  # или None для READ COMMITTED
    
    # Операции чтения - уровень по умолчанию
    return None


async def transaction_middleware(
    request: Request,
    call_next
) -> Response:
    container: AsyncContainer = request.app.state.dishka_container
    async with container() as request_container:
        transaction_manager = await request_container.get(ITransactionManager)

        isolation_level = _get_isolation_level_for_request(request)
        logger.debug(f"start transaction with isolation level: {isolation_level}")

        async with transaction_manager.transaction(isolation_level=isolation_level):
            response = await call_next(request)
            logger.debug(f"end transaction")

            return response
