from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.menu_category_interactor import AddMenuCategoryInteractor, GetMenuCategoryInteractor, GetRestaurantMenuCategoryInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.menu_category_repository import IMunuCategoryRepository


class MenuCategoryInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_menu_category_interactor(
        self,
        menu_category_repository: IMunuCategoryRepository
    ) -> GetMenuCategoryInteractor:
        return GetMenuCategoryInteractor(menu_category_repository)

    @provide(scope=Scope.REQUEST)
    async def get_restaurant_menu_category_interactor(
        self,
        menu_category_repository: IMunuCategoryRepository
    ) -> GetRestaurantMenuCategoryInteractor:
        return GetRestaurantMenuCategoryInteractor(menu_category_repository)

    @provide(scope=Scope.REQUEST)
    async def add_menu_category_interactor(
        self,
        menu_category_repository: IMunuCategoryRepository,
        transaction_manager: ITransactionManager,
    ) -> AddMenuCategoryInteractor:
        return AddMenuCategoryInteractor(menu_category_repository, transaction_manager)
