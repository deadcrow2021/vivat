from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from app.src.application.interfaces.interactors.food import GetFoodInteractor


router = APIRouter(prefix="/food", tags=["auth"])

@router.get(
    '/food',
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Food not found."},
    },
)
@inject
async def get_food(
    id: int,
    get_food: FromDishka[GetFoodInteractor]
):
    return {'id': id}