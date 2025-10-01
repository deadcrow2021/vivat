from sqlalchemy.exc import SQLAlchemyError

from src.domain.dto.city_dto import AddCityRequest, AddCityResponse, DeleteCityResponse, GetAllCitiesResponse, GetCityResponse, UpdateCityRequest, UpdateCityResponse
from src.application.exceptions import DatabaseException, IdNotValidError, UnhandledException
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import city_repository


class GetAllCitiesInteractor:
    def __init__(
        self, city_repository: city_repository.ICityRepository
    ):
        self._city_repository = city_repository

    async def __call__(self) -> GetAllCitiesResponse:
        cities = await self._city_repository.get_cities()
        data = [
                GetCityResponse(
                    id=c.id,
                    name=c.name,
                    coordinates=[float(c.latitude), float(c.longitude)]
                )
                for c in cities
            ]

        return GetAllCitiesResponse(data=data)


class GetCityInteractor:
    def __init__(
        self, city_repository: city_repository.ICityRepository
    ):
        self._city_repository = city_repository

    async def __call__(self, city_id: int) -> GetCityResponse:
        if city_id < 1:
            raise IdNotValidError

        city = await self._city_repository.get_city_by_id(city_id)
        
        return GetCityResponse(
            id=city.id,
            name=city.name,
            coordinates=[float(city.latitude), float(city.longitude)]
        )


class AddCityInteractor:
    def __init__(
        self, city_repository: city_repository.ICityRepository,
        transaction_manager: ITransactionManager
    ):
        self._city_repository = city_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, city_request: AddCityRequest) -> AddCityResponse:
        city = await self._city_repository.add_city(city_request)
        await self._transaction_manager.commit()

        return AddCityResponse(
            id=city.id,
            name=city.name,
            coordinates=[float(city.latitude), float(city.longitude)]
        )


class UpdateCityInteractor:
    def __init__(
        self, city_repository: city_repository.ICityRepository,
        transaction_manager: ITransactionManager
    ):
        self._city_repository = city_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, city_id: int, city_request: UpdateCityRequest) -> UpdateCityResponse:
        if city_id < 1:
            raise IdNotValidError

        city = await self._city_repository.get_city_by_id(city_id)
        updated_city = await self._city_repository.update_city(city, city_request)
        await self._transaction_manager.commit()

        return UpdateCityResponse(
            id=updated_city.id,
            name=updated_city.name,
            coordinates=[float(updated_city.latitude), float(updated_city.longitude)]
        )


class DeleteCityInteractor:
    def __init__(
        self, city_repository: city_repository.ICityRepository,
        transaction_manager: ITransactionManager
    ):
        self._city_repository = city_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, city_id: int) -> DeleteCityResponse:
        if city_id < 1:
            raise IdNotValidError

        city = await self._city_repository.get_city_by_id(city_id)
        delete_city_response = await self._city_repository.delete_city(city)
        await self._transaction_manager.commit()

        return delete_city_response
