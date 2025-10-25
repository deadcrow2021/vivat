import asyncio
from contextlib import asynccontextmanager
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from dishka import AsyncContainer
from telegram.ext import Application

from src.middlewares import exception_middleware, transaction_middleware
from src.exceptions import register_exception_handlers
from src.ioc.ioc_main import create_container
from src.config import Config, create_config
from src.infrastructure.adapters.controllers import (
    food_controller,
    restaurant_controller,
    city_controller,
    feature_controller,
    auth_controller,
    users_controller,
    menu_category_controller,
    food_variant_controller,
    food_characteristic_controller,
    ingredient_controller,
    user_address_controller,
    order_controller,
    order_item_controller
)


def setup_routers(app: FastAPI) -> None:
    app.include_router(food_controller.router, tags=["Food"])
    app.include_router(restaurant_controller.router, tags=["Restaurant"])
    app.include_router(city_controller.router, tags=["City"])
    app.include_router(feature_controller.router, tags=["Feature"])
    app.include_router(auth_controller.router, tags=["Auth"])
    app.include_router(users_controller.router, tags=["Users"])
    app.include_router(menu_category_controller.router, tags=["Menu Category"])
    app.include_router(food_variant_controller.router, tags=["Food Variant"])
    app.include_router(food_characteristic_controller.router, tags=["Food Characteristic"])
    app.include_router(ingredient_controller.router, tags=["Ingredient"])
    app.include_router(user_address_controller.router, tags=["User Address"])
    app.include_router(order_controller.router, tags=["Order"])
    app.include_router(order_item_controller.router, tags=["Order Item"])


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
    """Запускает Telegram бота в фоновом режиме"""
    try:
        telegram_app: Application = await container.get(Application)
        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.updater.start_polling()

        # Бесконечный цикл для поддержания работы бота
        while True:
            await asyncio.sleep(3600)  # Спим 1 час
    except Exception as e:
        print(f"Error starting Telegram bot: {e}")
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
    config: Config = create_config()
    app: FastAPI = FastAPI(
        lifespan=lifespan,
        root_path="/api",
        debug=True if config.app.environment == "development" else False
    )

    container: AsyncContainer = create_container()
    app.state.dishka_container = container
    setup_dishka(container, app)
    setup_middlewares(app, config)
    register_exception_handlers(app)
    setup_routers(app)

    return app


if __name__ == "__main__":
    config: Config = create_config()

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(create_application(), host="0.0.0.0", port=config.app.port)
