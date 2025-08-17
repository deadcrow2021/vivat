from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.city_dto import AddCityRequest, DeleteCityResponse, UpdateCityRequest
from src.infrastructure.drivers.db.tables import MenuCategory


class IMunuCategoryRepository(Protocol):
    @abstractmethod
    async def get_menu_categories(self) -> List[MenuCategory]:
        raise NotImplementedError

    @abstractmethod
    async def get_menu_categories_data(self, current_category: MenuCategory) -> MenuCategory:
        raise NotImplementedError