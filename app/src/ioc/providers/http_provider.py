from typing import AsyncIterator

from aiohttp import ClientSession
from dishka import Provider, Scope, provide

from src.infrastructure.adapters.notification.http_notifier import HttpOrderNotifier
from src.application.interfaces.notification.http_notifier import IHTTPOrderNotifier
from src.config import Config


class HTTPProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterator[ClientSession]:
        async with ClientSession() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_http_bot_notifier(
        self,
        session: ClientSession,
        config: Config
    ) -> IHTTPOrderNotifier:
        return HttpOrderNotifier(session, config)
