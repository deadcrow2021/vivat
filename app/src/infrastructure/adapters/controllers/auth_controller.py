from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from starlette import status

# from src.infrastructure.adapters.dependencies.auth_dependencies import get_current_user
from src.application.interfaces.interactors.auth_interactor import GetCurrentUserInteractor, LoginUserInteractor, LogoutInteractor, RegisterUserInteractor, UpdateAccessTokenInteractor
from src.domain.dto.auth_dto import CreateUser, CreateUserResponse, CurrentUserDTO, LogOutResponse, LoginUserRequest, LogInDTO, LoginUserResponse, TokenResponse, UpdateUserResponse

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
    register_user: FromDishka[RegisterUserInteractor],
    login_user: FromDishka[LoginUserInteractor],
    response: Response
):
    await register_user(user_create_request)
    resp = await login_user(
        LoginUserRequest(
                phone=user_create_request.phone,
                password=user_create_request.password
        ),
        response
    )

    return resp


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginUserResponse,
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
    response_model=UpdateUserResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Can't update access token."},
    },
)
@inject
async def update_access_token(
    update_token: FromDishka[UpdateAccessTokenInteractor],
    request: Request,
    response: Response
):
    return await update_token(request, response)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=LogOutResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"error": "Logout error."},
    },
)
@inject
async def logout(
    logout_: FromDishka[LogoutInteractor],
    request: Request,
    response: Response
):
    return await logout_(request, response)


@router.get("/profile", response_model=CurrentUserDTO)
@inject
async def get_current_user(
    current_user: FromDishka[GetCurrentUserInteractor],
    request: Request
):
    return await current_user(request)