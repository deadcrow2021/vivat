from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.ioc.providers.repositories import (
    restaurant_repository,
    food_repository,
    city_repository,
    feature_repository,
    auth_repository,
    users_repository,
    menu_category_repository
)
from src.ioc.providers.interactors import (
    restaurant_interactor,
    food_interactor,
    city_interactor,
    feature_interactor,
    auth_interactor,
    users_interactor,
    menu_category_interactor
)
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
        feature_interactor.FeatureInteractorProvider(),
        auth_interactor.AuthInteractorProvider(),
        users_interactor.UsersInteractorProvider(),
        menu_category_interactor.MenuCategoryInteractorProvider(),
        # Repositories
        restaurant_repository.RestaurantRepositryProvider(),
        food_repository.FoodRepositryProvider(),
        city_repository.CityRepositryProvider(),
        feature_repository.FeatureRepositryProvider(),
        auth_repository.AuthRepositryProvider(),
        users_repository.UsersRepositryProvider(),
        menu_category_repository.MenuCategoryRepositryProvider(),
        # Others
        ConfigProvider(),
    )
