from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.application.interfaces.interactors.food_variant_interactor import GetFoodVariantInteractor


router = APIRouter(prefix="/food_variant", tags=["Food Variant"])


@router.get(
    "/food_variant{variant_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Food variant not found."},
    },
)
@inject
async def get_food_variant(variant_id: int, get_food: FromDishka[GetFoodVariantInteractor]):
    return await get_food(variant_id)
