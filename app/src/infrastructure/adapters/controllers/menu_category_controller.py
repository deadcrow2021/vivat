from typing import Annotated, Optional
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query
from starlette import status

from src.domain.dto.menu_category_dto import AddMenuCategoryRequest, AddMenuCategoryResponse, HomePageResponse
from src.application.interfaces.interactors.menu_category_interactor import (
    AddMenuCategoryInteractor,
    GetMenuCategoryInteractor,
    GetRestaurantMenuCategoryInteractor
)


router = APIRouter(prefix="/category", tags=["Menu Category"])


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


# TODO: добавить проверку на роль админа
# @router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=AddMenuCategoryResponse,
#     responses={
#         status.HTTP_400_BAD_REQUEST: {"error": "Menu category haven't been created."},
#     },
# )
# @inject
# async def add_menu_category(
#     menu_category_request: AddMenuCategoryRequest,
#     add_category: FromDishka[AddMenuCategoryInteractor]
# ):
#     return await add_category(menu_category_request)
