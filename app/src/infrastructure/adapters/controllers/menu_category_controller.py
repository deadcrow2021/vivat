from typing import Annotated, Optional
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query
from starlette import status

from src.domain.dto.menu_category_dto import HomePageResponse
from src.application.interfaces.interactors.menu_category_interactor import (
    GetMenuCategoryInteractor,
    GetRestaurantMenuCategoryInteractor
)



router = APIRouter(prefix="/category", tags=["Menu Category"])

# TODO: add exceptions
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=HomePageResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Cannot get menu categories. Menu categories not found."},
    },
)
@inject
async def get_menu_category(
    get_menu_category_: FromDishka[GetMenuCategoryInteractor],
    category_id: Annotated[int | None, Query(alias="category_id", gt=0)] = None
):
    return await get_menu_category_(category_id)


@router.get(
    "/restaurant/{restaurant_id}",
    status_code=status.HTTP_200_OK,
    response_model=HomePageResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Cannot get menu categories. Menu categories not found."},
    },
)
@inject
async def get_restaurant_menu_category(
    get_restaurant_category: FromDishka[GetRestaurantMenuCategoryInteractor],
    restaurant_id: int,
    category_id: Annotated[int | None, Query(alias="category_id", gt=0)] = None
):
    return await get_restaurant_category(restaurant_id, category_id)
