from contextlib import asynccontextmanager
import asyncio
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from dishka import AsyncContainer
from telegram.ext import Application

from src.ioc.ioc_telegram import create_telegram_container
from src.exceptions import register_exception_handlers
from src.infrastructure.adapters.controllers import telegram_bot_controller
from src.middlewares import exception_middleware, transaction_middleware
from src.config import Config, create_config
from src.logger import logger


def setup_routers(app: FastAPI) -> None:
    app.include_router(telegram_bot_controller.router, tags=["TelegramBot"])


def setup_middlewares(app: FastAPI, config: Config) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.get_allow_origins,
        allow_methods=config.cors.get_allow_methods,
        allow_headers=config.cors.get_allow_headers,
        allow_credentials=config.cors.get_allow_credentials,
    )
    app.middleware("http")(transaction_middleware.transaction_middleware) # 1-й - оборачивает в транзакцию
    app.middleware("http")(exception_middleware.exception_middleware) # затем 2-й - перехватывает все ошибки


async def start_telegram_bot(container: AsyncContainer):
    """Запускает Telegram бота"""    
    try:
        telegram_app: Application = await container.get(Application)

        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.updater.start_polling()

        logger.info("Telegram bot started successfully!")
        
        # Бесконечный цикл для поддержания работы бота
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
    finally:
        if 'telegram_app' in locals():
            await telegram_app.updater.stop()
            await telegram_app.stop()
            await telegram_app.shutdown()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем Telegram бота в фоне
    container = app.state.dishka_container
    bot_task = asyncio.create_task(start_telegram_bot(container))

    yield

    # Останавливаем бота при завершении
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass


def create_application() -> FastAPI:
    config = create_config()
    app = FastAPI(
        root_path="/bot",
        lifespan=lifespan,
        debug=True if config.app.environment == "development" else False
    )

    container = create_telegram_container()
    app.state.dishka_container = container
    setup_dishka(container, app)
    setup_middlewares(app, config)
    register_exception_handlers(app)
    setup_routers(app)

    return app


if __name__ == "__main__":
    config = create_config()

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(create_application(), host="0.0.0.0", port=config.bot.bot_port)
