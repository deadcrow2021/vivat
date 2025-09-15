from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import VariantNotFoundError
from src.application.interfaces.repositories.food_characteristic_repository import IFoodCharacteristicRepository
from src.infrastructure.drivers.db.tables import FoodCharacteristic, FoodVariant


class FoodCharacteristicRepository(IFoodCharacteristicRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # TODO: divide by repositories
    async def add_characteristics_to_variant_by_id(self, variant_id: int, characteristic_value: str) -> FoodCharacteristic:
        stmt = select(FoodVariant).where(FoodVariant.id == variant_id).options(selectinload(FoodVariant.characteristics))
        result = await self._session.execute(stmt)
        variant = result.scalars().first()

        if not variant:
            raise VariantNotFoundError(id=variant_id)

        stmt_char = select(FoodCharacteristic).where(FoodCharacteristic.measure_value == characteristic_value)
        result_char = await self._session.execute(stmt_char)
        characteristic = result_char.scalars().first()

        if characteristic:
            variant.characteristics.append(characteristic)
        else:
            characteristic = FoodCharacteristic(measure_value=characteristic_value)
            variant.characteristics.append(characteristic)

        await self._session.flush()
        return characteristic
