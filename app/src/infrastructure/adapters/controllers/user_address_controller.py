from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.domain.dto.user_address_dto import AddUserAddressRequest, AddUserAddressResponse
from src.application.interfaces.interactors.user_address_interactor import AddUserAddressInteractor#, GetUserAddressInteractor



router = APIRouter(prefix="/user_address", tags=["User Address"])

# @router.get(
#     "/{address_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=...,
#     responses={
#         status.HTTP_404_NOT_FOUND: {"error": "City not found."},
#     },
# )
# @inject
# async def get_city_by_id(
#     city_id: int,
#     get_city: FromDishka[GetUserAddressInteractor]
# ):
#     return await get_city(city_id)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AddUserAddressResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "User address haven't been created."},
    },
)
@inject
async def add_user_address(
    user_request: AddUserAddressRequest,
    add_address: FromDishka[AddUserAddressInteractor]
):
    return await add_address(user_request)
