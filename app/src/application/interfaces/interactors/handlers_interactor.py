from telegram import Update
from telegram.ext import ContextTypes

from src.domain.dto.order_dto import OrderStatus
from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.application.interfaces.notification.notifier import IOrderNotifier
from src.application.interfaces.transaction_manager import ITransactionManager


class BotHandlerInteractor:
    def __init__(
        self,
        order_repository: IOrderRepository,
        notifier: IOrderNotifier,
        transaction_manager: ITransactionManager,
    ):
        self._order_repository = order_repository
        self._transaction_manager = transaction_manager
        self._notifier = notifier


    async def handle_order_callback(
        self,
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обрабатывает нажатия на кнопки изменения статуса заказа"""
        query = update.callback_query
        await query.answer()

        # Разбираем callback_data: order:{order_id}:{new_status}
        data_parts = query.data.split(':')
        if len(data_parts) != 3:
            return

        order_id = int(data_parts[1])
        new_status_code = data_parts[2]

        # Преобразуем код статуса в OrderStatus
        status_mapping = {
            "in_progress": OrderStatus.IN_PROGRESS,
            "in_delivery": OrderStatus.IN_DELIVERY, 
            "done": OrderStatus.DONE,
            "cancelled": OrderStatus.CANCELLED
        }

        if new_status_code not in status_mapping:
            return

        new_status = status_mapping[new_status_code]

        try:
            # Простейшие правила переходов: из CREATED -> IN_PROGRESS, IN_PROGRESS -> IN_DELIVERY|DONE, IN_DELIVERY -> DONE
            updated_order = await self._order_repository.update_order_status(order_id, new_status)
            await self._transaction_manager.commit()

            # Обновляем сообщение в Telegram
            message_text = query.message.text
            if '\n\nСтатус:' in message_text:
                message_text = message_text.split('\n\nСтатус:')[0]  # Получаем оригинальный текст без статуса

            await self._notifier.update_order_message(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                order_id=order_id,
                message_text=message_text,
                current_status=updated_order.status.value
            )

        except Exception as e:
            print(f"Error updating order status: {e}")
            await self._transaction_manager.rollback()
            await query.answer("Ошибка при обновлении статуса", show_alert=True)
