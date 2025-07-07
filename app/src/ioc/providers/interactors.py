from dishka import provide, Provider, Scope

from app.src.application.interfaces.interactors import food


class InteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_food_interactor(
        self
    ) -> food.GetFoodInteractor:
        return food.GetFoodInteractor()