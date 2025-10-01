from dishka import provide, Provider, Scope

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.interactors.food_variant_interactor import GetFoodVariantInteractor, GetMenuCategoryPositionsIngredientsInteractor
from src.application.interfaces.repositories.food_variant_repository import IFoodVariantRepository
from src.application.interfaces.repositories.menu_category_repository import IMunuCategoryRepository


class FoodVariantInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_food_variant_interactor(
        self,
        food_variant_repository: IFoodVariantRepository
    ) -> GetFoodVariantInteractor:
        return GetFoodVariantInteractor(food_variant_repository)

    @provide(scope=Scope.REQUEST)
    async def get_menu_category_food_variants_ingredients_interactor(
        self,
        food_variant_repository: IFoodVariantRepository,
        menu_category_repository: IMunuCategoryRepository
    ) -> GetMenuCategoryPositionsIngredientsInteractor:
        return GetMenuCategoryPositionsIngredientsInteractor(food_variant_repository, menu_category_repository)
