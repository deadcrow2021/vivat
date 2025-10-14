from typing import Annotated, List

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query
from starlette import status

from src.domain.dto.food_variant_dto import FoodVariantResponse, PositionsResponse
from src.infrastructure.drivers.db.tables import FoodVariant
from src.application.interfaces.interactors.food_variant_interactor import GetFoodVariantInteractor, GetMenuCategoryPositionsIngredientsInteractor


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


@router.get(
    "/category/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=PositionsResponse,
    responses={
        404: {"description": "Food variant not found."},
    },
)
@inject
async def get_menu_category_food_variants_ingredients(
    category_id: int,
    get_foods_ingredients: FromDishka[GetMenuCategoryPositionsIngredientsInteractor],
    restaurant_id: Annotated[int | None, Query(alias="restaurant_id", gt=0)] = None
):
    return await get_foods_ingredients(category_id, restaurant_id)
