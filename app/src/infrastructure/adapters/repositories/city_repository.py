from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.city_dto import AddCityRequest, DeleteCityResponse, UpdateCityRequest
from src.infrastructure.exceptions import CityNotFoundError
from src.application.interfaces.repositories.city_repository import (
    ICityRepository
)
from src.infrastructure.drivers.db.tables import City


class CityRepository(ICityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_cities(self) -> List[City]:
        city_query = select(City)
        city_result = await self._session.execute(city_query)
        cities = city_result.scalars().all()
        if not cities:
            raise CityNotFoundError()

        return cities

    async def get_city_by_id(self, city_id: int) -> City:
        city = await self._session.get(City, city_id)
        if not city:
            raise CityNotFoundError(id=city_id)

        return city

    async def add_city(self, city_request: AddCityRequest) -> City:
        new_city = City(
            name=city_request.name,
            latitude=city_request.latitude,
            longitude=city_request.longitude
        )

        self._session.add(new_city)
        await self._session.flush()

        return new_city

    async def update_city(self, city: City, city_request: UpdateCityRequest) -> City:
        update_dict = city_request.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(city, key, value)

        await self._session.flush()
        return city

    async def delete_city(self, city: City) -> DeleteCityResponse:
        await self._session.delete(city)
        await self._session.flush()

        return DeleteCityResponse(id=city.id)