from datetime import datetime
from typing import List
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.feature_dto import CreateFeatureRequest, DeleteFeatureResponse
from src.infrastructure.exceptions import FeatureNotFoundError
from src.logger import logger
from src.application.interfaces.repositories.feature_repository import IFeatureRepository
from src.infrastructure.drivers.db.tables import Feature


class FeatureRepository(IFeatureRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_feature_by_id(self, feature_id: int) -> Feature:
        feature = await self._session.get(Feature, feature_id)
        if not feature:
            raise FeatureNotFoundError(id=feature_id)

        return feature


    async def get_features(self) -> List[Feature]:
        feature_query = select(Feature)
        feature_result = await self._session.execute(feature_query)
        features = feature_result.scalars().all()

        if not features:
            raise FeatureNotFoundError()

        return features


    async def add_feature(self, feature_request: CreateFeatureRequest) -> Feature:
        feature = Feature(
            name=feature_request.name,
            icon_url=feature_request.icon_url
        )

        self._session.add(feature)
        await self._session.flush()

        return feature


    async def delete_feature(self, feature: Feature) -> DeleteFeatureResponse:
        await self._session.delete(feature)
        await self._session.flush()

        return DeleteFeatureResponse(id=feature.id)
