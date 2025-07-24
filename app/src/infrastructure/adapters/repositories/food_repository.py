from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.food_repository import IFoodRepository


class FoodRepository(IFoodRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, food_id: int):
        return {"id": 123}
        # return await self._session.get(User, user_id)
