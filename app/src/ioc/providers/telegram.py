from dishka import provide, Provider, Scope, AsyncContainer
from telegram import Bot, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from src.application.interfaces.repositories.chat_repository import IChatRepository
from src.application.interfaces.repositories.users_repository import IUsersRepository
from src.application.interfaces.interactors.handlers_interactor import BotHandlerInteractor
from src.application.interfaces.repositories.restaurant_repository import IRestaurantRepository
from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.infrastructure.adapters.telegram.order_notifier import TelegramOrderNotifier
from src.application.interfaces.notification.notifier import INotifier
from src.application.interfaces.transaction_manager import ITransactionManager
from src.config import Config


class TelegramProvider(Provider):
    @provide(scope=Scope.APP)
    async def telegram_bot(self, config: Config) -> Bot:
        return Bot(config.bot.bot_api_key)


    @provide(scope=Scope.REQUEST)
    async def order_notifier(
        self,
        bot: Bot,
        restaurant_repository: IRestaurantRepository
    ) -> INotifier:
        return TelegramOrderNotifier(bot, restaurant_repository)


    @provide(scope=Scope.REQUEST)
    async def bot_handler_interactor(
        self,
        transaction_manager: ITransactionManager,
        order_repository: IOrderRepository,
        users_repository: IUsersRepository,
        chat_repository: IChatRepository,
        notifier: INotifier,
    ) -> BotHandlerInteractor:
        return BotHandlerInteractor(
            transaction_manager,
            order_repository,
            users_repository,
            chat_repository,
            notifier
        )


    @provide(scope=Scope.APP)
    async def telegram_application(
        self,
        config: Config,
        bot: Bot,
        container: 'AsyncContainer'  # Добавляем контейнер для создания зависимостей при запросах
    ) -> Application:
        """Создает и настраивает Telegram Application с хэндлерами"""
        application = Application.builder().token(config.bot.bot_api_key).build()

        # Сохраняем контейнер в данных бота для использования в обработчиках
        application.bot_data['container'] = container

        # Добавляем обработчик команды /get_chat_id
        application.add_handler(CommandHandler("get_chat_id", self._create_chat_id_handler()))

        # Добавляем обработчик команды /ban
        application.add_handler(CommandHandler("ban", self._create_ban_handler()))

        # Добавляем обработчик callback запросов от кнопок заказа
        application.add_handler(
            CallbackQueryHandler(
                self._create_order_callback_handler(),
                pattern="^order:"
            )
        )

        # Добавляем обработчик для заблокированных кнопок
        application.add_handler(CallbackQueryHandler(
            lambda update, context: update.callback_query.answer("Этот статус уже установлен"),
            pattern="^disabled$"
        ))

        return application

    def _create_ban_handler(self):
        """Создает обработчик для команды /ban"""
        async def ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Получаем контейнер из данных бота
            container = context.bot_data['container']
            
            # Создаем новый контекст запроса для обработки команды
            async with container() as request_container:
                handler: BotHandlerInteractor = await request_container.get(BotHandlerInteractor)
                await handler.handle_ban_command(update, context)
        
        return ban_handler

    def _create_chat_id_handler(self):
        """Создает обработчик для команды /get_chat_id"""
        async def chat_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat = update.effective_chat
            chat_id = chat.id
            chat_title = chat.title if chat.title else "личный чат"
            chat_type = chat.type
            
            message = (
                f"📋 Информация о чате:\n"
                f"🆔 ID чата: <code>{chat_id}</code>\n"
                f"📛 Название: {chat_title}\n"
                f"🔰 Тип: {chat_type}\n\n"
                f"💡 Этот ID можно использовать для настройки уведомлений о заказах"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
        
        return chat_id_handler


    def _create_order_callback_handler(self):
        """Создает обработчик для callback запросов"""
        async def order_callback_handler(update, context):
            # Получаем контейнер из данных бота
            container = context.bot_data['container']
            
            # Создаем новый контекст запроса для обработки callback
            async with container() as request_container:
                handler = await request_container.get(BotHandlerInteractor)
                await handler.handle_order_callback(update, context)

        return order_callback_handler
