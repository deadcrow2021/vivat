from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.domain.dto.restaurant_dto import (
    AddRestaurantRequest,
    AddRestaurantResponse,
    DeleteRestaurantResponse,
    GetRestaurantsResponse,
    UpdateRestaurantRequest,
)
from src.application.interfaces.interactors.restaurant_interactor import (
    ChangeRestaurantInteractor,
    DeleteRestaurantInteractor,
    GetRestaurantInteractor,
    CreateRestaurantInteractor,
)


router = APIRouter(prefix="/restaurant", tags=["Restaurant"])


@router.get(
    "/{city_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetRestaurantsResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Restaurants not found."},
    },
)
@inject
async def get_restaurant_by_city_id(
    city_id: int, get_restaurants: FromDishka[GetRestaurantInteractor]
):
    return await get_restaurants(city_id)


@router.post(
    "/{city_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=AddRestaurantResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Restaurant haven't been created."},
    },
)
@inject
async def create_restaurant_by_city_id(
    city_id: int,
    restaurant: AddRestaurantRequest,
    add_restaurant: FromDishka[CreateRestaurantInteractor],
):
    return await add_restaurant(city_id, restaurant)


@router.patch(
    "/{restaurant_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=AddRestaurantResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Restaurant haven't been changed."},
    },
)
@inject
async def change_restaurant_by_id(
    restaurant_id: int,
    restaurant: UpdateRestaurantRequest,
    change_restaurant: FromDishka[ChangeRestaurantInteractor],
):
    return await change_restaurant(restaurant_id, restaurant)


@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteRestaurantResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Restaurant haven't been deleted."},
    },
)
@inject
async def delete_restaurant_by_id(
    restaurant_id: int, delete_restaurant: FromDishka[DeleteRestaurantInteractor]
):
    return await delete_restaurant(restaurant_id)
