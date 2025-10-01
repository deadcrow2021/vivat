from sqlalchemy.exc import SQLAlchemyError

from src.domain.dto.feature_dto import BaseFeatureResponse, CreateFeatureRequest, CreateFeatureResponse, DeleteFeatureResponse, GetFeatureResponse, GetAllFeaturesResponse
from src.application.exceptions import DatabaseException, IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import feature_repository


class GetFeatureInteractor:
    def __init__(
        self, feature_repository: feature_repository.IFeatureRepository
    ):
        self._feature_repository = feature_repository

    async def __call__(self, feature_id: int) -> GetFeatureResponse:
        if feature_id < 1:
            raise IdNotValidError
            
        feature = await self._feature_repository.get_feature_by_id(feature_id)

        return GetFeatureResponse(
            id=feature.id,
            name=feature.name,
            icon_url=feature.icon_url
        )


class GetAllFeaturesInteractor:
    def __init__(
        self, feature_repository: feature_repository.IFeatureRepository
    ):
        self._feature_repository = feature_repository

    async def __call__(self) -> GetAllFeaturesResponse:
        features = await self._feature_repository.get_features()
        data = [
            BaseFeatureResponse(
                id=feature.id,
                name=feature.name,
                icon_url=feature.icon_url
            ) 
            for feature in features
        ]

        return GetAllFeaturesResponse(data=data)


class AddFeatureInteractor:
    def __init__(
        self, feature_repository: feature_repository.IFeatureRepository,
        transaction_manager: ITransactionManager
    ):
        self._feature_repository = feature_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, feature_request: CreateFeatureRequest) -> CreateFeatureResponse:
        feature = await self._feature_repository.add_feature(feature_request)
        await self._transaction_manager.commit()

        return CreateFeatureResponse(
            id=feature.id,
            name=feature.name,
            icon_url=feature.icon_url
        )


class DeleteFeatureInteractor:
    def __init__(
        self, feature_repository: feature_repository.IFeatureRepository,
        transaction_manager: ITransactionManager
    ):
        self._feature_repository = feature_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, feature_id: int) -> DeleteFeatureResponse:
        if feature_id < 1:
            raise IdNotValidError

        feature = await self._feature_repository.get_feature_by_id(feature_id)
        feature_response = await self._feature_repository.delete_feature(feature)
        await self._transaction_manager.commit()

        return feature_response
