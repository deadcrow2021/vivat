from typing import Union
from src.domain.dto.menu_category_dto import CategoryItem, HomeData, HomePageResponse
from src.domain.dto.city_dto import AddCityRequest, AddCityResponse, GetAllCitiesResponse, GetCityResponse, UpdateCityRequest, UpdateCityResponse
from src.application.exceptions import IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import menu_category_repository


class GetMenuCategoryInteractor:
    def __init__(
        self, menu_category_repository: menu_category_repository.IMunuCategoryRepository
    ):
        self._menu_category_repository = menu_category_repository

    async def __call__(self, category_id: Union[int, None]) -> GetCityResponse:
        categories = await self._menu_category_repository.get_menu_categories()
        if category_id: ### TODO: Add exception if category not found by id
            current_category = next(
                (
                    category for category in categories
                    if category.id == category_id
                ),
                None
            )
            if not current_category:
                raise ValueError(f"Category with id {category_id} not found")
        else:
            current_category = categories[0]
        
        positions = await self._menu_category_repository.get_menu_category_positions(current_category)

        category_items = [
            CategoryItem(
                id=category.id,
                name=category.name,
                # need_addings=any(food.ingredient_associations for food in category.foods)
            )
            for category in categories
        ]

        return HomePageResponse(
            date=HomeData(
                categories=category_items,
                positions=positions
            )
        )



class GetRestaurantMenuCategoryInteractor:
    def __init__(
        self, menu_category_repository: menu_category_repository.IMunuCategoryRepository
    ):
        self._menu_category_repository = menu_category_repository

    async def __call__(self, category_id: Union[int, None]) -> GetCityResponse:
        categories = await self._menu_category_repository.get_menu_categories()
        
        return HomePageResponse(
            date=HomeData(
                # categories=category_items,
                # positions=positions
            )
        )