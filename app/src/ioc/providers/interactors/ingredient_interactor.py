from dishka import provide, Provider, Scope

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.interactors.ingredient_interactor import GetAllIngredientsInteractor, GetMenuCategoryIngredientsInteractor
from src.application.interfaces.repositories.ingredient_repository import IIngredientRepository


class IngredientInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_ingredients_interactor(
        self,
        ingredient_repository: IIngredientRepository
    ) -> GetAllIngredientsInteractor:
        return GetAllIngredientsInteractor(ingredient_repository)

    @provide(scope=Scope.REQUEST)
    async def get_all_default_category_ingredients_interactor(
        self,
        ingredient_repository: IIngredientRepository
    ) -> GetMenuCategoryIngredientsInteractor:
        return GetMenuCategoryIngredientsInteractor(ingredient_repository)
