from src.application.interfaces.notification.notifier import INotifier
from src.domain.dto.telegram_dto import SendOrderInfo, TelegramResponse, UpdateOrderInfo


class SendOrderToTelegramInteractor:
    def __init__(
        self,
        notifier: INotifier
    ):
        self._notifier = notifier

    async def __call__(self, order_info: SendOrderInfo) -> TelegramResponse:
        await self._notifier.send_new_order(
            restaurant_id=order_info.restaurant_id,
            order_id=order_info.order_id,
            message_text=order_info.message_text,
            current_status=order_info.current_status,
            action=order_info.action,
        )

        return TelegramResponse(message='success')


class UpdateOrderInTelegramInteractor:
    def __init__(
        self,
        notifier: INotifier
    ):
        self._notifier = notifier

    async def __call__(self, order_info: UpdateOrderInfo) -> TelegramResponse:
        await self._notifier.update_order_message(
            chat_id=order_info.chat_id,
            message_id=order_info.message_id,
            order_id=order_info.order_id,
            message_text=order_info.message_text,
            current_status=order_info.current_status,
            action=order_info.action,
        )

        return TelegramResponse(message='success')
