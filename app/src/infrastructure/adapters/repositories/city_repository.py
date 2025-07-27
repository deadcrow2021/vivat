from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import CityNotFoundError
from src.application.interfaces.repositories.city_repository import (
    ICityRepository
)
from src.infrastructure.drivers.db.tables import City


class CityRepository(ICityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_city_by_id(self, city_id: int) -> City:
        city = await self._session.get(City, city_id)
        if not city:
            raise CityNotFoundError(id=city_id)

        return city
