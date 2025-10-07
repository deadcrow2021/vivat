from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.ioc.providers.repositories import (
    restaurant_repository,
    food_repository,
    city_repository,
    feature_repository,
    auth_repository,
    users_repository,
    menu_category_repository,
    food_variant_repository,
    food_characteristic_repository,
    ingredient_repository,
    user_address_repository,
    order_repository,
    order_item_repository
)
from src.ioc.providers.interactors import (
    restaurant_interactor,
    food_interactor,
    city_interactor,
    feature_interactor,
    auth_interactor,
    users_interactor,
    menu_category_interactor,
    food_variant_interactor,
    food_characteristic_interactor,
    ingredient_interactor,
    user_address_interactor,
    order_interactor,
    order_item_interactor
)
from src.ioc.providers.database import DatabaseProvider
from src.ioc.providers.config import ConfigProvider
from src.ioc.providers.telegram import TelegramProvider


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
        food_variant_interactor.FoodVariantInteractorProvider(),
        food_characteristic_interactor.FoodCharacteristicInteractorProvider(),
        ingredient_interactor.IngredientInteractorProvider(),
        user_address_interactor.UserAddressInteractorProvider(),
        order_interactor.OrderInteractorProvider(),
        order_item_interactor.OrderItemInteractorProvider(),
        # Repositories
        restaurant_repository.RestaurantRepositryProvider(),
        food_repository.FoodRepositryProvider(),
        city_repository.CityRepositryProvider(),
        feature_repository.FeatureRepositryProvider(),
        auth_repository.AuthRepositryProvider(),
        users_repository.UsersRepositryProvider(),
        menu_category_repository.MenuCategoryRepositryProvider(),
        food_variant_repository.FoodVariantRepositryProvider(),
        food_characteristic_repository.FoodCharacteristicRepositoryProvider(),
        ingredient_repository.IngredientRepositryProvider(),
        user_address_repository.UserAddressRepositryProvider(),
        order_repository.OrderRepositryProvider(),
        order_item_repository.OrderItemRepositryProvider(),
        # Others
        ConfigProvider(),
        TelegramProvider(),
    )
