from typing import List

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request
from starlette import status

from src.domain.dto.city_dto import DeleteCityResponse
from src.application.interfaces.interactors.auth_interactor import GetCurrentUserInteractor
from src.domain.dto.user_address_dto import AddUserAddressRequest, AddUserAddressResponse, GetUserAddress, UpdateUserAddressRequest
from src.application.interfaces.interactors.user_address_interactor import AddUserAddressInteractor, DeleteAddressInteractor, GetUserAddressInteractor, UpdateUserAddressInteractor#, GetUserAddressInteractor



router = APIRouter(prefix="/user_address", tags=["User Address"])

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[GetUserAddress],
    responses={
        status.HTTP_404_NOT_FOUND: {"error": "Address not found."},
    },
)
@inject
async def get_user_address(
    user: FromDishka[GetCurrentUserInteractor],
    get_address: FromDishka[GetUserAddressInteractor],
    request: Request
):
    user_dto = await user(request)
    return await get_address(user_dto.id)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AddUserAddressResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "User address haven't been created."},
    },
)
@inject
async def add_user_address(
    user_request: AddUserAddressRequest,
    user: FromDishka[GetCurrentUserInteractor],
    add_address: FromDishka[AddUserAddressInteractor],
    request: Request
):
    user_dto = await user(request)
    return await add_address(user_dto.id, user_request)


@router.patch(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    response_model=AddUserAddressResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "User address haven't been updated."},
    },
)
@inject
async def update_user_address(
    address_id: int,
    user_request: UpdateUserAddressRequest,
    user: FromDishka[GetCurrentUserInteractor],
    update_address: FromDishka[UpdateUserAddressInteractor],
    request: Request
):
    user_dto = await user(request)
    return await update_address(address_id, user_dto.id, user_request)


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteCityResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Address haven't been deleted."},
    },
)
@inject
async def delete_address(
    address_id: int,
    user: FromDishka[GetCurrentUserInteractor],
    delete_city: FromDishka[DeleteAddressInteractor],
    request: Request
):
    user_dto = await user(request)
    return await delete_city(user_dto.id, address_id)
