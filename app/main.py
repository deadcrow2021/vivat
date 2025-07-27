import asyncio
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from dishka import AsyncContainer

from src.exceptions import register_exception_handlers
from src.ioc.ioc_main import create_container
from src.config import Config, create_config
from src.infrastructure.adapters.controllers import (
    food_controller,
    restaurant_controller,
    city_controller
)


def setup_routers(app: FastAPI) -> None:
    app.include_router(food_controller.router, tags=["Food"])
    app.include_router(restaurant_controller.router, tags=["Restaurant"])
    app.include_router(city_controller.router, tags=["City"])


def setup_middlewares(app: FastAPI, config: Config) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            # "http://frontend:3000"  # Docker сеть
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # BaseHTTPMiddleware,
        # SessionMiddleware(session_config=config.session)
    )


def create_application() -> FastAPI:
    config: Config = create_config()
    app: FastAPI = FastAPI(
        # title=config.app.title,
        # debug=config.app.debug
    )

    container: AsyncContainer = create_container()
    setup_dishka(container, app)
    setup_routers(app)
    setup_middlewares(app, config)
    register_exception_handlers(app)

    return app


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run(create_application(), host="0.0.0.0", port=8000)
