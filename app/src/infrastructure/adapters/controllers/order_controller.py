from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request
from starlette import status

from src.application.interfaces.interactors.auth_interactor import GetCurrentUserInteractor
from src.application.interfaces.interactors.order_interactor import AddOrderInteractor
from src.domain.dto.order_dto import OrderRequest, CreateOrderResponse


router = APIRouter(prefix="/order", tags=["Order"])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateOrderResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Order haven't been created."},
    },
)
@inject
async def add_order(
    order_request: OrderRequest,
    user: FromDishka[GetCurrentUserInteractor],
    add_order: FromDishka[AddOrderInteractor],
    request: Request
):
    user_dto = await user(request)
    return await add_order(order_request, user_dto.id)
