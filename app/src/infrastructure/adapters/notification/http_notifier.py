from typing import List
import json

import aiohttp
from aiohttp import ClientError, ClientSession, ServerConnectionError

from src.application.interfaces.notification.http_notifier import IHTTPOrderNotifier
from src.domain.enums.enums import OrderAction
from src.config import Config
from src.logger import logger


class HttpOrderNotifier(IHTTPOrderNotifier):
    def __init__(self, session: ClientSession, config: Config):
        self._session = session
        self._config = config

    async def send_order_info_to_bot(
        self,
        restaurant_id: int,
        order_id: int,
        message_text: str,
        current_status: str,
        action: OrderAction
    ) -> None:
        """Отправляет уведомление о новом заказе в сервис бота через HTTP"""
        payload = {
            "restaurant_id": restaurant_id,
            "order_id": order_id,
            "message_text": message_text,
            "current_status": current_status,
            "action": action.value
        }

        try:
            async with self._session.post(
                f"{self._config.bot.get_bot_app_url}/bot/notifications/order",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 201:
                    logger.warning(f"Failed to send notification: {response.status}")
        except Exception as e:
            logger.error(f"Error sending HTTP notification: {e}")

        return {'success': True}


    async def update_order_message(
        self,
        chat_id: int,
        message_id: int,
        order_id: int,
        message_text: str,
        current_status: str,
        action: OrderAction
    ) -> None:
        """Обновляет сообщение с заказом через сервис бота"""
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "order_id": order_id,
            "message_text": message_text,
            "current_status": current_status,
            "action": action.value
        }

        try:
            async with self._session.post(
                f"{self._config.bot.get_bot_app_url}/bot/notifications/order/update",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    logger.warning(f"Failed to update notification: {response.status}")
        except Exception as e:
            logger.error(f"Error updating HTTP notification: {e}")
        
        return {'success': True}
