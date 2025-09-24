from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status

from src.application.interfaces.interactors.users_interactor import GetUserInteractor
from src.domain.dto.users_dto import GetUserResponse



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
