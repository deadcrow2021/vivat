from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.menu_category_dto import AddMenuCategoryRequest#, PositionItem
from src.infrastructure.drivers.db.tables import MenuCategory


class IMunuCategoryRepository(Protocol):
    @abstractmethod
    async def get_menu_categories(self) -> List[MenuCategory]:
        raise NotImplementedError

    @abstractmethod
    async def get_menu_category_by_id(self, category_id: int) -> MenuCategory:
        raise NotImplementedError

    @abstractmethod
    async def get_menu_category_positions(self, current_category: MenuCategory) -> MenuCategory:
        raise NotImplementedError

    async def get_restaurant_menu_categories(self, restaurant_id: int) -> List[MenuCategory]:
        raise NotImplementedError

    # async def get_restaurant_menu_category_positions(self, restaurant_id: int, current_category: MenuCategory) -> List[PositionItem]:
    #     raise NotImplementedError

    async def add_menu_category(self, menu_category_request: AddMenuCategoryRequest) -> MenuCategory:
        raise NotImplementedError
