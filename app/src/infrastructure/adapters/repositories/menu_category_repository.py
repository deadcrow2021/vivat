from typing import List, Optional, Union
from sqlalchemy import and_, select, or_
from sqlalchemy.orm import contains_eager, joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import MenuCategoryNotFoundError
from src.domain.dto.menu_category_dto import AddMenuCategoryRequest #, AddingItem, PositionItem, SizeInfo
from src.application.interfaces.repositories.menu_category_repository import IMunuCategoryRepository
from src.infrastructure.drivers.db.tables import (
    Food,
    FoodIngredientAssociation,
    FoodVariant,
    Ingredient,
    MenuCategory,
    Restaurant,
    restaurant_food_disabled
)


class MenuCategoryRepository(IMunuCategoryRepository): # TODO: add exceptions
    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def add_menu_category(self, menu_category_request: AddMenuCategoryRequest) -> MenuCategory:
        stmt = (
            select(MenuCategory)
            .order_by(MenuCategory.display_order.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        last_category = result.scalars().first() # TODO: Вынести в отдельную функцию

        new_category = MenuCategory(
            name=menu_category_request.name,
            display_order=last_category.display_order + 1 if last_category else 1
        )

        self._session.add(new_category)
        await self._session.flush()

        return new_category


    async def get_menu_category_by_id(self, category_id: int) -> MenuCategory:
        stmt = (
            select(MenuCategory)
            .where(MenuCategory.id == category_id)
        )
        result = await self._session.execute(stmt)
        category = result.scalars().first()
        
        if not category:
            raise MenuCategoryNotFoundError(id=category_id)

        return category


    async def get_menu_categories(self, category_id: Optional[int] = None) -> List[MenuCategory]:
        stmt = (
            select(MenuCategory)
            .order_by(MenuCategory.display_order.asc())
        )
        result = await self._session.execute(stmt)
        categories = result.scalars().all()

        if category_id:
            current_category = next(
                (
                    category for category in categories
                    if category.id == category_id
                ),
                None
            )
            if not current_category:
                raise MenuCategoryNotFoundError(id=category_id)

        if not categories:
            raise MenuCategoryNotFoundError

        return categories


    async def get_menu_category_positions(self, current_category: MenuCategory) -> MenuCategory:
        if not current_category:
            raise MenuCategoryNotFoundError

        # Реализация без фильтрации по ресторану (оригинальная)
        stmt = (
            select(MenuCategory)
            .outerjoin(MenuCategory.foods)
            .outerjoin(Food.variants)
            .outerjoin(FoodVariant.characteristics)
            .outerjoin(Food.ingredient_associations)
            .outerjoin(FoodIngredientAssociation.ingredient)
            .options(
                contains_eager(MenuCategory.foods)
                .contains_eager(Food.variants)
                .contains_eager(FoodVariant.characteristics),

                contains_eager(MenuCategory.foods)
                .contains_eager(Food.ingredient_associations)
                .contains_eager(FoodIngredientAssociation.ingredient)
            )
            .where(MenuCategory.id == current_category.id)
            .where(FoodVariant.is_active == True)
            .where(
                FoodIngredientAssociation.ingredient.has(Ingredient.is_available == True),
                FoodIngredientAssociation.is_default == True
            )
        )
        result = await self._session.execute(stmt)
        category_info = result.unique().scalars().one_or_none()
        
        return category_info


    async def get_restaurant_menu_categories(self, restaurant_id: int) -> List[MenuCategory]:
        """Получает категории меню для конкретного ресторана"""
        stmt = (
            select(MenuCategory)
            .join(MenuCategory.restaurants)
            .where(Restaurant.id == restaurant_id)
            .where(Restaurant.is_active == True)
            .order_by(MenuCategory.display_order.asc())
        )
        result = await self._session.execute(stmt)
        categories = result.scalars().all()
        
        if not categories:
            raise MenuCategoryNotFoundError
        
        return categories


    async def get_restaurant_menu_category_positions(
        self,
        current_category: MenuCategory,
        restaurant_id: int
    ) -> MenuCategory:
        """Получает позиции меню для категории с учетом отключенных блюд в ресторане"""
        # Создаем алиас для таблицы отключенных блюд
        disabled_alias = aliased(restaurant_food_disabled)

        stmt = (
            select(MenuCategory)
            .join(MenuCategory.foods)
            .outerjoin(Food.variants)
            .outerjoin(FoodVariant.characteristics)
            .outerjoin(Food.ingredient_associations)
            .outerjoin(FoodIngredientAssociation.ingredient)
            .outerjoin(
                disabled_alias,
                and_(
                    disabled_alias.c.restaurant_id == restaurant_id,
                    disabled_alias.c.food_id == Food.id
                )
            )
            .options(
                contains_eager(MenuCategory.foods)
                .contains_eager(Food.variants)
                .contains_eager(FoodVariant.characteristics),
                contains_eager(MenuCategory.foods)
                .contains_eager(Food.ingredient_associations)
                .contains_eager(FoodIngredientAssociation.ingredient)
            )
            .where(MenuCategory.id == current_category.id)
            .where(FoodVariant.is_active == True)
            .where(
                FoodIngredientAssociation.ingredient.has(Ingredient.is_available == True),
                FoodIngredientAssociation.is_default == True
            )
            .where(disabled_alias.c.food_id.is_(None))  # Исключаем отключенные блюда
        )

        result = await self._session.execute(stmt)
        category = result.unique().scalar_one_or_none()
        
        return category
