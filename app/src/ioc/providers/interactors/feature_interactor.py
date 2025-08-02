from dishka import provide, Provider, Scope

from src.application.interfaces.interactors.feature_interactor import AddFeatureInteractor, DeleteFeatureInteractor, GetFeatureInteractor, GetAllFeaturesInteractor
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories.feature_repository import IFeatureRepository


class FeatureInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_feature_interactor(
        self, feature_repository: IFeatureRepository
    ) -> GetFeatureInteractor:
        return GetFeatureInteractor(feature_repository)

    @provide(scope=Scope.REQUEST)
    async def get_features_interactor(
        self, feature_repository: IFeatureRepository
    ) -> GetAllFeaturesInteractor:
        return GetAllFeaturesInteractor(feature_repository)

    @provide(scope=Scope.REQUEST)
    async def add_feature_interactor(
        self,
        feature_repository: IFeatureRepository,
        transaction_manager: ITransactionManager,
    ) -> AddFeatureInteractor:
        return AddFeatureInteractor(feature_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    async def delete_feature_interactor(
        self,
        feature_repository: IFeatureRepository,
        transaction_manager: ITransactionManager,
    ) -> DeleteFeatureInteractor:
        return DeleteFeatureInteractor(feature_repository, transaction_manager)
