from dishka import Provider, Scope, provide

from src.application.interfaces.interactors.telegram_bot_interactor import SendOrderToTelegramInteractor
from src.application.interfaces.notification.notifier import INotifier


class TelegramBotOrderProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def add_order_interactor(
        self,
        notifier: INotifier,
    ) -> SendOrderToTelegramInteractor:
        return SendOrderToTelegramInteractor(
            notifier
        )
