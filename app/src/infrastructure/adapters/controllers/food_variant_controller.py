from typing import List

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.domain.dto.food_variant_dto import FoodVariantResponse
from src.infrastructure.drivers.db.tables import FoodVariant
from src.application.interfaces.interactors.food_variant_interactor import GetFoodVariantInteractor


router = APIRouter(prefix="/food_variant", tags=["Food Variant"])


@router.get(
    "/{food_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[FoodVariantResponse],
    responses={
        404: {"description": "Food variant not found."},
    },
)
@inject
async def get_food_variant(food_id: int, get_food: FromDishka[GetFoodVariantInteractor]):
    return await get_food(food_id)
