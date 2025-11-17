from dishka import AsyncContainer, make_async_container

from src.ioc.providers.telegram_bot_order_provider import TelegramBotOrderProvider
from src.ioc.providers.database import DatabaseProvider
from src.ioc.providers.config import ConfigProvider
from src.ioc.providers.telegram import TelegramProvider
from src.ioc.providers.repositories import (
    restaurant_repository,
    chat_repository,
    order_repository,
    users_repository,
)


def create_telegram_container() -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(),
        ConfigProvider(),
        TelegramProvider(),
        restaurant_repository.RestaurantRepositryProvider(),
        chat_repository.ChatRepositryProvider(),
        order_repository.OrderRepositryProvider(),
        users_repository.UsersRepositryProvider(),
        TelegramBotOrderProvider(),
    )