from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.feature_repository import IFeatureRepository
from src.infrastructure.adapters.repositories.feature_repository import FeatureRepository


class FeatureRepositryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_feature_repository(
        self, session: AsyncSession
    ) -> IFeatureRepository:
        return FeatureRepository(session)
