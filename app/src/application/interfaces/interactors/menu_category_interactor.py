from typing import List, Union

from sqlalchemy.exc import SQLAlchemyError

from src.infrastructure.drivers.db.tables import MenuCategory
from src.domain.dto.menu_category_dto import AddMenuCategoryRequest, AddMenuCategoryResponse, CategoryItem, HomeData, HomePageResponse
from src.application.exceptions import DatabaseException, IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import menu_category_repository


class GetMenuCategoryInteractor:
    def __init__(
        self, menu_category_repository: menu_category_repository.IMunuCategoryRepository
    ):
        self._menu_category_repository = menu_category_repository

    async def __call__(self, category_id: Union[int, None]) -> HomePageResponse:
        if category_id and category_id < 1:
            raise IdNotValidError

        try:
            # получаю список категорий
            categories: List[MenuCategory] = await self._menu_category_repository.get_menu_categories(category_id)

            # если передан id активной категории
            if category_id:
                current_category = next(
                    (
                        category for category in categories
                        if category.id == category_id
                    ),
                    None
                )
            else:
                # если id не передан, то беру первую категорию по display_order
                current_category = categories[0]

            positions = await self._menu_category_repository.get_menu_category_positions(current_category)

            category_items = [
                CategoryItem(
                    id=category.id,
                    name=category.name,
                    need_addings=category.need_addings
                )
                for category in categories
            ]

            return HomePageResponse(
                date=HomeData(
                    categories=category_items,
                    positions=positions
                )
            )

        except SQLAlchemyError:
            raise DatabaseException("Не удалось получить информацию о категории меню из базы данных")


class GetRestaurantMenuCategoryInteractor:
    def __init__(
        self, menu_category_repository: menu_category_repository.IMunuCategoryRepository
    ):
        self._menu_category_repository = menu_category_repository

    async def __call__(
        self,
        restaurant_id: int,
        category_id: Union[int, None] = None
    ) -> HomePageResponse:
        if restaurant_id < 1:
            raise IdNotValidError
        if category_id and category_id < 1:
            raise IdNotValidError

        try:
            # Получаем категории для конкретного ресторана
            categories = await self._menu_category_repository.get_restaurant_menu_categories(restaurant_id)

            # Выбираем текущую категорию
            if category_id:
                current_category = next(
                    (category for category in categories if category.id == category_id),
                    None
                )
                if not current_category:
                    raise ValueError(f"Категория с id {category_id} не найдена")
            else:
                current_category = categories[0]

            # Получаем позиции для текущей категории с учетом отключенных блюд
            positions = await self._menu_category_repository.get_restaurant_menu_category_positions(
                restaurant_id,
                current_category
            )

            # Формируем список категорий для ответа
            category_items = [
                CategoryItem(
                    id=category.id,
                    name=category.name,
                    need_addings=category.need_addings
                )
                for category in categories
            ]

            return HomePageResponse(
                date=HomeData(
                    categories=category_items,
                    positions=positions
                )
            )
        
        except SQLAlchemyError:
            raise DatabaseException("Не удалось получить информацию о категории меню указанного ресторана из базы данных")


class AddMenuCategoryInteractor:
    def __init__(
        self,
        menu_category_repository: menu_category_repository.IMunuCategoryRepository,
        transaction_manager: ITransactionManager
    ):
        self._menu_category_repository = menu_category_repository
        self._transaction_manager = transaction_manager

    async def __call__(
        self,
        menu_category_request: AddMenuCategoryRequest
    ) -> AddMenuCategoryResponse:
        try:
            category = await self._menu_category_repository.add_menu_category(menu_category_request)
            await self._transaction_manager.commit()

            return AddMenuCategoryResponse(
                id=category.id,
                name=category.name,
                display_order=category.display_order
            )
        except SQLAlchemyError:
            raise DatabaseException("Не удалось добавить категорию меню в базу данных")
