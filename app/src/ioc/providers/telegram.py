from dishka import provide, Provider, Scope, AsyncContainer
from telegram import Bot
from telegram.ext import Application, CallbackQueryHandler

from src.application.interfaces.interactors.handlers_interactor import BotHandlerInteractor
from src.application.interfaces.repositories.restaurant_repository import IRestaurantRepository
from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.infrastructure.adapters.telegram.order_notifier import TelegramOrderNotifier
from src.application.interfaces.notification.notifier import IOrderNotifier
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
    ) -> IOrderNotifier:
        return TelegramOrderNotifier(bot, restaurant_repository)


    @provide(scope=Scope.REQUEST)
    async def bot_handler_notifier(
        self,
        order_repository: IOrderRepository,
        notifier: IOrderNotifier,
        transaction_manager: ITransactionManager        
    ) -> BotHandlerInteractor:
        return BotHandlerInteractor(order_repository, notifier, transaction_manager)


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
