from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.application.interfaces.interactors.city_interactor import GetCityInteractor
from src.domain.dto.city_dto import GetCityResponse



router = APIRouter(prefix="/city", tags=["City"])


@router.get(
    "/{city_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetCityResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "City not found."},
    },
)
@inject
async def get_city_by_id(
    city_id: int,
    get_city: FromDishka[GetCityInteractor]
):
    return await get_city(city_id)