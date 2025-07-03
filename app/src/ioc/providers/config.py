from dishka import Provider, Scope, provide
from src.config import Config

class ConfigProvider(Provider):

    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return Config()
