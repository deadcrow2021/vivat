from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.application.interfaces.interactors.city_interactor import AddCityInteractor, DeleteCityInteractor, GetAllCitiesInteractor, GetCityInteractor, UpdateCityInteractor
from src.domain.dto.city_dto import AddCityRequest, AddCityResponse, DeleteCityResponse, GetAllCitiesResponse, GetCityResponse, UpdateCityRequest



router = APIRouter(prefix="/city", tags=["City"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=GetAllCitiesResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Cities not found."},
    },
)
@inject
async def get_city(
    get_cities: FromDishka[GetAllCitiesInteractor]
):
    return await get_cities()


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


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AddCityResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "City haven't been created."},
    },
)
@inject
async def add_city(
    city_request: AddCityRequest,
    add_city: FromDishka[AddCityInteractor]
):
    return await add_city(city_request)


@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AddCityResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "City haven't been changed."},
    },
)
@inject
async def update_city(
    city_id: int,
    city_request: UpdateCityRequest,
    update_city: FromDishka[UpdateCityInteractor]
):
    return await update_city(city_id, city_request)


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=DeleteCityResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "City haven't been deleted."},
    },
)
@inject
async def delete_city(
    city_id: int,
    delete_city: FromDishka[DeleteCityInteractor]
):
    return await delete_city(city_id)