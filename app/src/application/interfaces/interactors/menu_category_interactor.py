from src.domain.dto.city_dto import AddCityRequest, AddCityResponse, GetAllCitiesResponse, GetCityResponse, UpdateCityRequest, UpdateCityResponse
from src.application.exceptions import IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import menu_category_repository


class GetMenuCategoryInteractor:
    def __init__(
        self, menu_category_repository: menu_category_repository.IMunuCategoryRepository
    ):
        self._menu_category_repository = menu_category_repository

    async def __call__(self) -> GetCityResponse:
        categories = await self._menu_category_repository.get_menu_categories()
        if not categories:
            raise ValueError("Menu categories not found") ### Change

        data = await self._menu_category_repository.get_menu_categories_data(categories[0])
        
        return data