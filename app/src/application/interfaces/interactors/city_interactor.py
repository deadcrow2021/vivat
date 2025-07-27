from src.domain.dto.city_dto import GetCityResponse
from src.application.exceptions import IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import city_repository


class GetCityInteractor:
    def __init__(
        self, city_repository: city_repository.ICityRepository
    ):
        self._city_repository = city_repository

    async def __call__(self, city_id: int) -> GetCityResponse:
        if city_id < 1:
            raise IdNotValidError

        city = (
            await self._city_repository.get_city_by_id(city_id)
        )
        
        return GetCityResponse(
            name=city.name,
            coordiantes=[float(city.latitude), float(city.longitude)]
        )
