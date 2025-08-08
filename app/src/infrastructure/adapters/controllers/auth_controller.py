from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from starlette import status

from src.application.interfaces.interactors.auth_interactor import LoginUserInteractor, RegisterUserInteractor, UpdateAccessTokenInteractor
from src.domain.dto.auth_dto import CreateUser, CreateUserResponse, LoginUserRequest, TokenDTO, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "User haven't been registered."},
    },
)
@inject
async def register(
    user_create_request: CreateUser,
    register_user: FromDishka[RegisterUserInteractor]
):
    return await register_user(user_create_request)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Can't get access token."},
    },
)
@inject
async def login_for_access_token(
    login_user_request: LoginUserRequest,
    login_user: FromDishka[LoginUserInteractor],
    response: Response
):
    return await login_user(login_user_request, response)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Can't update access token."},
    },
)
@inject
async def update_access_token(
    update_token: FromDishka[UpdateAccessTokenInteractor],
    request: Request
):
    return await update_token(request)
