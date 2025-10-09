from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request, Response
from starlette import status

from src.application.interfaces.interactors.auth_interactor import GetCurrentUserInteractor, LogoutInteractor
from src.application.interfaces.interactors.users_interactor import DeleteUserInteractor, GetUserInteractor
from src.domain.dto.users_dto import DeleteUserResponse, GetUserResponse



router = APIRouter(prefix="/users", tags=["Users"])

# TODO: возможно нужно добавить проверку на роль админа
# @router.get(
#     "/{user_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=GetUserResponse,
#     responses={
#         status.HTTP_404_NOT_FOUND: {"error": "User not found."},
#     },
# )
# @inject
# async def get_user_by_id(
#     user_id: int,
#     get_user: FromDishka[GetUserInteractor]
# ):
#     return await get_user(user_id)

@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=DeleteUserResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "User have not been deleted."},
    },
)
@inject
async def delete_user(
    user: FromDishka[GetCurrentUserInteractor],
    delete_user: FromDishka[DeleteUserInteractor],
    logout_: FromDishka[LogoutInteractor],
    request: Request,
    response: Response
):
    user_dto = await user(request)
    delete_resp = await delete_user(user_dto.id)
    await logout_(request, response)

    return delete_resp
