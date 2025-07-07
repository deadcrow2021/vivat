import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from dishka import AsyncContainer

from src.ioc.ioc_main import create_container
from src.config import Config, create_config
from app.src.infrastructure.adapters.controllers import food


def setup_routers(app: FastAPI) -> None:
    app.include_router(food.router)


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
    # register_exception_handlers(app)

    # map_tables()

    return app

# @app.get("/", response_class=HTMLResponse)
# async def get_main_page(request: Request):
#     return 

if __name__ == "__main__":
    uvicorn.run(create_application(), host="0.0.0.0", port=8000)
