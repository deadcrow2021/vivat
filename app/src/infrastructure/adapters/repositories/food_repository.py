from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import FoodNotFoundError, MenuCategoryNotFoundError
from src.domain.dto.food_dto import AddFoodRequest
from src.infrastructure.drivers.db.tables import Food, MenuCategory
from src.application.interfaces.repositories.food_repository import IFoodRepository


class FoodRepository(IFoodRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_food_by_id(self, food_id: int) -> Food:
        stmt = (
            select(Food)
            .where(Food.id == food_id)
        )
        result = await self._session.execute(stmt)
        food = result.scalars().first()

        if not food:
            raise FoodNotFoundError(id=food_id)

        return food


    async def add_food_to_category(
        self,
        menu_category_id: int,
        food_request: AddFoodRequest
        ) -> Food:
        stmt = (
            select(MenuCategory)
            .where(MenuCategory.id == menu_category_id)
        )
        result = await self._session.execute(stmt)
        menu_category = result.scalars().one_or_none()

        if not menu_category:
            raise MenuCategoryNotFoundError(id=menu_category_id)

        new_food = Food(
            category_id=menu_category.id,
            name=food_request.name,
            image_url=food_request.image_url,
            description=food_request.description,
            measure_name=food_request.measure_name,
        )

        self._session.add(new_food)
        await self._session.flush()

        return new_food
