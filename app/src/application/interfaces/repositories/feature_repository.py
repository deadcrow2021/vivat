from abc import abstractmethod
from typing import List, Protocol

from src.domain.dto.feature_dto import CreateFeatureRequest, DeleteFeatureResponse
from src.infrastructure.drivers.db.tables import Feature


class IFeatureRepository(Protocol):
    @abstractmethod
    async def get_feature_by_id(self, feature_id: int) -> Feature:
        raise NotImplementedError

    @abstractmethod
    async def get_features(self) -> List[Feature]:
        raise NotImplementedError

    @abstractmethod
    async def add_feature(self, feature_request: CreateFeatureRequest) -> Feature:
        raise NotImplementedError

    @abstractmethod
    async def delete_feature(self, feature: Feature) -> DeleteFeatureResponse:
        raise NotImplementedError
