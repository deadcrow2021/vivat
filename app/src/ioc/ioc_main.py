from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.ioc.providers.interactors import InteractorProvider
from src.config import Config
from src.ioc.providers.database import DatabaseProvider
from src.ioc.providers.config import ConfigProvider

def create_container() -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        DatabaseProvider(),

        InteractorProvider(),

        ConfigProvider(),
    )
