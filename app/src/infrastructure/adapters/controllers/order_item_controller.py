from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from app.src.domain.dto.order_item_dto import AddOrderItemRequest, AddOrderItemResponse
from src.application.interfaces.interactors.order_item_interactor import AddOrderItemInteractor


router = APIRouter(prefix="/order_item", tags=["Order Item"])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AddOrderItemResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Order item haven't been created."},
    },
)
@inject
async def add_order_item(
    order_item_request: AddOrderItemRequest,
    add_item: FromDishka[AddOrderItemInteractor]
):
    return await add_item(order_item_request)
