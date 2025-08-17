from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.menu_category_repository import IMunuCategoryRepository
from src.infrastructure.adapters.repositories.menu_category_repository import MenuCategoryRepository


class MenuCategoryRepositryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_menu_category_repository(
        self, session: AsyncSession
    ) -> IMunuCategoryRepository:
        return MenuCategoryRepository(session)
