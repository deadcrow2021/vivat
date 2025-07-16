from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.ioc.providers.repositories import RepositriesProvider
from src.ioc.providers.interactors import InteractorProvider
from src.ioc.providers.database import DatabaseProvider
from src.ioc.providers.config import ConfigProvider

def create_container() -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        DatabaseProvider(),

        InteractorProvider(),
        RepositriesProvider(),

        ConfigProvider(),
    )
