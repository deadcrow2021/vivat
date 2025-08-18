from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.domain.dto.food_characteristic_dto import (
    AddCharacteristicsToVariantRequest,
    AddCharacteristicsToVariantResponse
)
from src.application.interfaces.interactors.food_characteristic_interactor import (
    AddCharacteristicsToVariantInteractor
)


router = APIRouter(prefix="/food_characteristic", tags=["Food Characteristic"])

# TODO: add exceptions
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AddCharacteristicsToVariantResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Cannot add characteristics to variant."},
    },
)
@inject
async def add_char_to_variant(
    add_char_request: AddCharacteristicsToVariantRequest,
    add_char: FromDishka[AddCharacteristicsToVariantInteractor]
):
    return add_char(add_char_request)