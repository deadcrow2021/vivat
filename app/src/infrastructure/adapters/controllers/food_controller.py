from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.domain.dto.food_dto import AddFoodRequest
from src.application.interfaces.interactors.food_interactor import AddFoodInteractor, GetFoodInteractor


router = APIRouter(prefix="/food", tags=["Food"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Food not found."},
    },
)
@inject
async def get_food(id: int, get_food: FromDishka[GetFoodInteractor]):
    return await get_food(id)


@router.post(
    "/category/{menu_category_id}",
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Food not created."},
    },
)
@inject
async def add_food_to_menu_category(
    menu_category_id: int,
    food_request: AddFoodRequest,
    add_food: FromDishka[AddFoodInteractor]
):
    return await add_food(menu_category_id, food_request)
