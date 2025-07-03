from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette import status


router = APIRouter(prefix="/auth", tags=["auth"])

@router.get(
    '/food',
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Food not found."},
    },
)
@inject
async def get_food(id: int):
    return {'id': id}