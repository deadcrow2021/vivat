from telegram import Update
from telegram.ext import ContextTypes

from src.domain.dto.order_dto import OrderStatus
from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.application.interfaces.repositories.chat_repository import IChatRepository
from src.application.interfaces.notification.notifier import INotifier
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.users_repository import IUsersRepository


class BotHandlerInteractor:
    def __init__(
        self,
        transaction_manager: ITransactionManager,
        order_repository: IOrderRepository,
        users_repository: IUsersRepository,
        chat_repository: IChatRepository,
        notifier: INotifier,
    ):
        self._transaction_manager = transaction_manager
        self._order_repository = order_repository
        self._users_repository = users_repository
        self._chat_repository = chat_repository
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
            await self._transaction_manager.rollback()
            await query.answer("Ошибка при обновлении статуса", show_alert=True)


    async def handle_ban_command(
        self,
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обрабатывает команду /ban для блокировки пользователей по номеру телефона"""
        chat_obj = update.effective_chat
        chat_id = str(chat_obj.id)
        
        chat = await self._chat_repository.get_chat(chat_id)
        if not chat:
            await update.message.reply_text("❌ Этот чат не поддерживается")
            return

        # Проверяем, что команда вызвана в групповом чате
        if update.effective_chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ Эта команда доступна только в групповых чатах")
            return

        # Проверяем, что пользователь является администратором
        try:
            chat_member = await context.bot.get_chat_member(
                update.effective_chat.id, 
                update.effective_user.id
            )
            if chat_member.status not in ['administrator', 'creator']:
                await update.message.reply_text("❌ Только администраторы могут использовать эту команду")
                return
        except Exception as e:
            await update.message.reply_text("❌ Ошибка проверки прав администратора")
            return

        # Получаем номер телефона из аргументов команды
        if not context.args:
            await update.message.reply_text(
                "ℹ️ Использование:\n"
                "/ban +79XXXXXXXXX\n\n"
                "Укажите номер телефона пользователя для блокировки"
            )
            return

        phone = context.args[0].strip()

        try:
            # Банним пользователя в базе данных по номеру телефона
            user = await self._users_repository.get_user_by_phone(phone)
            if not user:
                await update.message.reply_text("❌ Ошибка при блокировке пользователя. Пользователь не найден")
                return

            await self._users_repository.ban_user(user)
            await self._transaction_manager.commit()

            await update.message.reply_text(
                f"✅ Пользователь с номером {phone} заблокирован в системе\n\n"
                f"Теперь он не сможет создавать новые заказы."
            )
        except Exception as e:
            await self._transaction_manager.rollback()
            await update.message.reply_text("❌ Ошибка при блокировке пользователя")
