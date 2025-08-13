from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession



# class DependeciesProvider(Provider):

#     @provide(scope=Scope.REQUEST)
#     async def get_user_by_token_repository(
#         self, session: AsyncSession
#     ) -> IFeatureRepository:
#         return FeatureRepository(session)