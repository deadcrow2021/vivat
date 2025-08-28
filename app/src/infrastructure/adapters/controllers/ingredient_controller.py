from typing import List
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.application.interfaces.interactors.ingredient_interactor import GetAllIngredientsInteractor, GetMenuCategoryIngredientsInteractor
from src.domain.dto.ingredient_dto import IngredientResponse


router = APIRouter(prefix="/ingredient", tags=["Ingredient"])

# TODO: add exceptions
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=IngredientResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Ingredients not found."},
    },
)
@inject
async def get_all_ingredients(
    get_ingredients: FromDishka[GetAllIngredientsInteractor]
):
    return await get_ingredients()


@router.get(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[IngredientResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Ingredients not found."},
    },
)
@inject
async def get_all_ingredients(
    category_id: int,
    get_category_ingredients: FromDishka[GetMenuCategoryIngredientsInteractor]
):
    return await get_category_ingredients(category_id)
