from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request
from starlette import status

from src.application.interfaces.interactors.telegram_bot_interactor import SendOrderToTelegramInteractor, UpdateOrderInTelegramInteractor
from src.domain.dto.telegram_dto import SendOrderInfo, TelegramResponse, UpdateOrderInfo


router = APIRouter(prefix="/notifications", tags=["TelegramBot"])

@router.post(
    "/order",
    status_code=status.HTTP_201_CREATED,
    response_model=TelegramResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Can't create order message."},
    },
)
@inject
async def send_order_to_telegram(
    order_info: SendOrderInfo,
    send_order: FromDishka[SendOrderToTelegramInteractor],
):
    return await send_order(order_info)

@router.post(
    "/order/update",
    status_code=status.HTTP_200_OK,
    response_model=TelegramResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Can't update order message."},
    },
)
@inject
async def send_order_to_telegram(
    order_info: UpdateOrderInfo,
    update_order: FromDishka[UpdateOrderInTelegramInteractor],
):
    return await update_order(order_info)
