from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.menu_category_dto import AddingItem, CategoryItem, HomeData, HomePageResponse, PositionItem, SizeInfo
from src.application.interfaces.repositories.menu_category_repository import IMunuCategoryRepository
from src.infrastructure.drivers.db.tables import Food, FoodIngredientAssociation, FoodVariant, Ingredient, MenuCategory


class MenuCategoryRepository(IMunuCategoryRepository): # TODO: add exceptions
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        

    async def get_menu_categories(self) -> List[MenuCategory]:
        stmt = (
            select(MenuCategory)
            .order_by(MenuCategory.display_order.asc())
        )
        result = await self._session.execute(stmt)
        categories = result.scalars().all()
        
        if not categories:
            raise ValueError("Menu categories not found") ### Change
        
        return categories


    async def get_menu_category_positions(self, current_category: MenuCategory) -> List[PositionItem]:
        stmt = (
            select(MenuCategory)
            .order_by(MenuCategory.display_order.asc())
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
            .where(FoodVariant.is_active == True)  # Фильтрация неактивных вариантов сразу в БД
            .where(FoodIngredientAssociation.ingredient.has(Ingredient.is_available == True))  # Только доступные ингредиенты
        )

        result = await self._session.execute(stmt)
        categories = result.unique().scalars().all()

        if not categories:
            return HomePageResponse(date=None)

        positions = []
        for food in current_category.foods:
            if not food.variants:  # Пропускаем если нет активных вариантов
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
