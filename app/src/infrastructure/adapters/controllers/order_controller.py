from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.application.interfaces.interactors.order_interactor import AddOrderInteractor
from src.domain.dto.order_dto import OrderResponse


router = APIRouter(prefix="/order", tags=["Order"])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Order haven't been created."},
    },
)
@inject
async def add_order(
    order_response: OrderResponse,
    add_order: FromDishka[AddOrderInteractor]
):
    return add_order(order_response)
