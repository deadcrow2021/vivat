from dishka import provide, Provider, Scope


class RepositriesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_repositories(self) -> None:
        pass