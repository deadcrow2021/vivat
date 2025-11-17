from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.error import BadRequest

from src.domain.enums.enums import OrderAction
from src.application.interfaces.notification.notifier import INotifier
from src.application.interfaces.repositories.restaurant_repository import IRestaurantRepository


class TelegramOrderNotifier(INotifier):
    def __init__(
        self,
        bot: Bot,
        restaurant_repository: IRestaurantRepository
    ) -> None:
        self._bot = bot
        self._restaurants = restaurant_repository


    async def send_new_order(
        self,
        restaurant_id: int,
        order_id: int,
        message_text: str,
        current_status: str,
        action: OrderAction
    ) -> None:
        restaurant = await self._restaurants.get_restaurant_by_id(restaurant_id)
        chats = restaurant.telegram_chats
        if not chats:
            return

        keyboard = self._build_keyboard(current_status, order_id, action)
        full_text = f"{message_text}\n\nСтатус: {self._get_status_display(current_status)}"

        for chat in chats:
            try:
                await self._bot.send_message(
                    chat_id=chat.chat_id,
                    text=full_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
            except BadRequest:
                continue


    async def update_order_message(
        self,
        chat_id: int,
        message_id: int,
        order_id: int,
        message_text: str,
        current_status: str,
        action: OrderAction
    ) -> None:
        """Обновляет сообщение с заказом после изменения статуса"""
        try:
            keyboard = self._build_keyboard(current_status, order_id, action)
            full_text = f"{message_text}\n\nСтатус: {self._get_status_display(current_status)}"

            await self._bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=full_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except BadRequest as e:
            # Если сообщение не найдено или другие ошибки
            print(f"Error updating message: {e}")


    def _build_keyboard(
        self,
        status: str,
        order_id: int,
        action: OrderAction
    ) -> List[List[InlineKeyboardButton]]:
        def mk(text: str, code: str):
            if code == status:
                return InlineKeyboardButton(f"✅ {text}", callback_data="disabled")
            return InlineKeyboardButton(text, callback_data=f"order:{order_id}:{code}")

        return [
            [
                mk("В работе", "in_progress"),
                mk("В доставке", "in_delivery") if action == OrderAction.DELIVERY else mk("Готово к выдаче", "cooked"),
            ],
            [
                mk("Готово", "done"),
                mk("Отмена", "cancelled"),
            ]
        ]


    def _get_status_display(self, status: str) -> str:
        """Возвращает читаемое отображение статуса"""
        status_map = {
            "created": "🆕 Создан",
            "in_progress": "👨‍🍳 В процессе",
            "in_delivery": "🚗 В доставке",
            "cooked": "🍽️ Готово к выдаче",
            "done": "✅ Выполнено",
            "cancelled": "❌ Отмена",
        }
        return status_map.get(status, status)
