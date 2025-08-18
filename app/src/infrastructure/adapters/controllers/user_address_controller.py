from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.domain.dto.user_address_dto import AddUserAddressRequest, AddUserAddressResponse
from src.application.interfaces.interactors.user_address_interactor import AddUserAddressInteractor



router = APIRouter(prefix="/user_address", tags=["User Address"])

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
