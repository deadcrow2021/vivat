from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.domain.dto.feature_dto import CreateFeatureRequest, CreateFeatureResponse, DeleteFeatureResponse, GetFeatureResponse, GetAllFeaturesResponse
from src.application.interfaces.interactors.feature_interactor import AddFeatureInteractor, DeleteFeatureInteractor, GetAllFeaturesInteractor, GetFeatureInteractor


router = APIRouter(prefix="/feature", tags=["Feature"])

# TODO: add exceptions
@router.get(
    "/{feature_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetFeatureResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Feature not found."},
    },
)
@inject
async def get_feature(
    feature_id: int,
    get_feature_: FromDishka[GetFeatureInteractor]
):
    return await get_feature_(feature_id)

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=GetAllFeaturesResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Features not found."},
    },
)
@inject
async def get_all_features(
    get_features: FromDishka[GetAllFeaturesInteractor]
):
    return await get_features()

# TODO: нужна проверка на роль админа
# @router.post(
#     "",
#     status_code=status.HTTP_201_CREATED,
#     response_model=CreateFeatureResponse,
#     responses={
#         status.HTTP_404_NOT_FOUND: {"error": "Feature haven't been created."},
#     },
# )
# @inject
# async def create_feature(
#     feature_request: CreateFeatureRequest,
#     create_feature_: FromDishka[AddFeatureInteractor]
# ):
#     return await create_feature_(feature_request)

# TODO: нужна проверка на роль админа
# @router.delete( 
#     "/{feature_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=DeleteFeatureResponse,
#     responses={
#         status.HTTP_404_NOT_FOUND: {"error": "Features haven't been deleted."},
#     },
# )
# @inject
# async def delete_feature(
#     feature_id: int,
#     delete_feature: FromDishka[DeleteFeatureInteractor]
# ):
#     return await delete_feature(feature_id)
