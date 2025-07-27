from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.ioc.providers.repositories import restaurant_repository, food_repository, city_repository
from src.ioc.providers.interactors import restaurant_interactor, food_interactor, city_interactor
from src.ioc.providers.database import DatabaseProvider
from src.ioc.providers.config import ConfigProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        DatabaseProvider(),
        # Interactors
        restaurant_interactor.RestaurantInteractorProvider(),
        food_interactor.FoodInteractorProvider(),
        city_interactor.CityInteractorProvider(),
        # Repositories
        restaurant_repository.RestaurantRepositryProvider(),
        food_repository.FoodRepositryProvider(),
        city_repository.CityRepositryProvider(),
        # Others
        ConfigProvider(),
    )
