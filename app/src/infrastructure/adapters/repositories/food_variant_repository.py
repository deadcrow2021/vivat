from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import VariantNotFoundError
from src.application.interfaces.repositories.food_variant_repository import IFoodVariantRepository
from src.infrastructure.drivers.db.tables import FoodVariant


class FoodVariantRepository(IFoodVariantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_variants_by_food_id(self, food_id: int) -> List[FoodVariant]:
        stmt = select(FoodVariant).where(FoodVariant.food_id == food_id)
        result = await self._session.execute(stmt)
        variants = result.scalars().all()

        if not variants:
            raise VariantNotFoundError()

        return variants
