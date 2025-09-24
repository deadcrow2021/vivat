from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from starlette import status

from src.logger import logger
from src.domain.dto.restaurant_dto import (
    AddRestaurantRequest,
    AddRestaurantResponse,
    DeleteRestaurantResponse,
    GetCityRestaurantsResponse,
    GetRestaurantResponse,
    UpdateRestaurantRequest,
)
from src.application.interfaces.interactors.restaurant_interactor import (
    UpdateRestaurantInteractor,
    DeleteRestaurantInteractor,
    GetCityRestaurantsInteractor,
    CreateRestaurantInteractor,
    GetRestaurantInteractor,
)


router = APIRouter(prefix="/restaurant", tags=["Restaurant"])


@router.get(
    "/{restaurant_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetRestaurantResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Restaurant not found."},
    },
)
@inject
async def get_restaurant_by_id(
    restaurant_id: int,
    get_restaurant: FromDishka[GetRestaurantInteractor]
):
    return await get_restaurant(restaurant_id)


@router.get(
    "/city/{city_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetCityRestaurantsResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Restaurants not found."},
    },
)
@inject
async def get_restaurant_by_city_id(
    city_id: int,
    get_city_restaurants: FromDishka[GetCityRestaurantsInteractor]
):
    return await get_city_restaurants(city_id)


# TODO: нужна проверка на роль админа
# @router.post(
#     "/{city_id}",
#     status_code=status.HTTP_201_CREATED,
#     response_model=AddRestaurantResponse,
#     responses={
#         status.HTTP_400_BAD_REQUEST: {"error": "Restaurant haven't been created."},
#     },
# )
# @inject
# async def create_restaurant_by_city_id(
#     city_id: int,
#     restaurant: AddRestaurantRequest,
#     add_restaurant: FromDishka[CreateRestaurantInteractor],
# ):
#     return await add_restaurant(city_id, restaurant)


# @router.patch(
#     "/{restaurant_id}",
#     status_code=status.HTTP_201_CREATED,
#     response_model=AddRestaurantResponse,
#     responses={
#         status.HTTP_400_BAD_REQUEST: {"error": "Restaurant haven't been changed."},
#     },
# )
# @inject
# async def update_restaurant_by_id(
#     restaurant_id: int,
#     restaurant: UpdateRestaurantRequest,
#     change_restaurant: FromDishka[UpdateRestaurantInteractor],
# ):
#     return await change_restaurant(restaurant_id, restaurant)


# @router.delete(
#     "/{restaurant_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=DeleteRestaurantResponse,
#     responses={
#         status.HTTP_400_BAD_REQUEST: {"error": "Restaurant haven't been deleted."},
#     },
# )
# @inject
# async def delete_restaurant_by_id(
#     restaurant_id: int, delete_restaurant: FromDishka[DeleteRestaurantInteractor]
# ):
#     return await delete_restaurant(restaurant_id)
