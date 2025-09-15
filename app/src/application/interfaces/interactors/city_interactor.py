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
        try:
            cities = await self._city_repository.get_cities()
            data = [
                    GetCityResponse(
                        id=c.id,
                        name=c.name,
                        coordiantes=[float(c.latitude), float(c.longitude)]
                    )
                    for c in cities
                ]
            return GetAllCitiesResponse(data=data)

        except SQLAlchemyError:
            raise DatabaseException("Failed to get all cities in db")


class GetCityInteractor:
    def __init__(
        self, city_repository: city_repository.ICityRepository
    ):
        self._city_repository = city_repository

    async def __call__(self, city_id: int) -> GetCityResponse:
        if city_id < 1:
            raise IdNotValidError
        try:

            city = await self._city_repository.get_city_by_id(city_id)
            
            return GetCityResponse(
                id=city.id,
                name=city.name,
                coordiantes=[float(city.latitude), float(city.longitude)]
            )
        
        except SQLAlchemyError:
            raise DatabaseException("Failed to get city in db")


class AddCityInteractor:
    def __init__(
        self, city_repository: city_repository.ICityRepository,
        transaction_manager: ITransactionManager
    ):
        self._city_repository = city_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, city_request: AddCityRequest) -> AddCityResponse:
        try:
            city = await self._city_repository.add_city(city_request)
            await self._transaction_manager.commit()

            return AddCityResponse(
                id=city.id,
                name=city.name,
                coordiantes=[float(city.latitude), float(city.longitude)]
            )

        except SQLAlchemyError:
            raise DatabaseException("Failed to add city in db")


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
        try:

            city = await self._city_repository.get_city_by_id(city_id)
            updated_city = await self._city_repository.update_city(city, city_request)
            await self._transaction_manager.commit()

            return UpdateCityResponse(
                id=updated_city.id,
                name=updated_city.name,
                coordiantes=[float(updated_city.latitude), float(updated_city.longitude)]
            )

        except SQLAlchemyError:
            raise DatabaseException("Failed to update city in db")


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
        try:
            city = await self._city_repository.get_city_by_id(city_id)
            delete_city_response = await self._city_repository.delete_city(city)
            await self._transaction_manager.commit()

            return delete_city_response
    
        except SQLAlchemyError:
            raise DatabaseException("Failed to delete city in db")
