from typing import List
from sqlalchemy import and_, select, or_
from sqlalchemy.orm import contains_eager, joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.menu_category_dto import AddMenuCategoryRequest, AddingItem, PositionItem, SizeInfo
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
        last_category = result.scalars().one_or_none() # TODO: Вынести в отдельную функцию

        if not last_category:
            raise ValueError("Категории меню не найдены") # TODO: Change

        new_category = MenuCategory(
            name=menu_category_request.name,
            display_order=last_category.display_order + 1
        )

        self._session.add(new_category)
        await self._session.flush()

        return new_category


    async def get_menu_categories(self) -> List[MenuCategory]:
        stmt = (
            select(MenuCategory)
            .order_by(MenuCategory.display_order.asc())
        )
        result = await self._session.execute(stmt)
        categories = result.scalars().all()
        
        if not categories:
            raise ValueError("Категории меню не найдены") ### Change
        
        return categories


    async def get_menu_category_positions(self, current_category: MenuCategory) -> List[PositionItem]:
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
            .where(FoodIngredientAssociation.ingredient.has(Ingredient.is_available == True))
        )

        result = await self._session.execute(stmt)
        categories = result.unique().scalars().one_or_none()

        if not categories:
            return []

        positions = []
        for food in current_category.foods:
            if not food.variants:
                continue

            size_info = [
                SizeInfo(
                    measure_value=int(variant.characteristics[0].measure_value) if variant.characteristics else 0,
                    price=float(variant.price),
                    price_multiplier=float(variant.ingredient_price_modifier)
                )
                for variant in food.variants
            ]

            ingredients = []
            for assoc in food.ingredient_associations or []:
                ingredient = assoc.ingredient
                ingredients.append(
                    AddingItem(
                        id=ingredient.id,
                        name=ingredient.name,
                        image_url=ingredient.image_url or "",
                        price=float(ingredient.price)
                    )
                )

            positions.append(
                PositionItem(
                    id=food.id,
                    name=food.name,
                    image_url=food.image_url or "",
                    description=food.description or "",
                    measure_name=food.measure_name or "",
                    size=size_info,
                    ingredients=ingredients
                )
            )
        
        return positions


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
            raise ValueError("Для данного ресторана нет категорий меню") # TODO: Change
        
        return categories

    async def get_restaurant_menu_category_positions(self, restaurant_id: int, current_category: MenuCategory) -> List[PositionItem]:
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
            .where(FoodIngredientAssociation.ingredient.has(Ingredient.is_available == True))
            .where(disabled_alias.c.food_id.is_(None))  # Исключаем отключенные блюда
        )

        result = await self._session.execute(stmt)
        category = result.unique().scalar_one_or_none()

        if not category or not category.foods:
            return []

        positions = []
        for food in category.foods:
            if not food.variants:
                continue

            # Преобразуем варианты в SizeInfo
            size_info = [
                SizeInfo(
                    measure_value=int(variant.characteristics[0].measure_value) if variant.characteristics else 0,
                    price=float(variant.price),
                    price_multiplier=float(variant.ingredient_price_modifier)
                )
                for variant in food.variants
            ]

            ingredients = []
            for assoc in food.ingredient_associations or []:
                ingredient = assoc.ingredient
                ingredients.append(
                    AddingItem(
                        id=ingredient.id,
                        name=ingredient.name,
                        image_url=ingredient.image_url or "",
                        price=float(ingredient.price)
                    )
                )

            positions.append(
                PositionItem(
                    id=food.id,
                    name=food.name,
                    image_url=food.image_url or "",
                    description=food.description or "",
                    measure_name=food.measure_name or "",
                    size=size_info,
                    ingredients=ingredients
                )
            )
        
        return positions
