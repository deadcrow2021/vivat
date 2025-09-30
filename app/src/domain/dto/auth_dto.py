import re
from typing import Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator

from src.domain.mixins.phone_validator import PhoneValidatorMixin


class BaseUserRequest(PhoneValidatorMixin, BaseModel):
    phone: str = Field(..., max_length=20)
    password: str = Field(..., min_length=8, max_length=16)

    @field_validator("password")
    def validate_password(cls, v: str):
        if len(v) < 8 or len(v) > 16:
            raise RequestValidationError("Пароль должен быть от 8 до 16 символов")

        # TODO: Потом включить проверку
        # if any(c.isalpha() and not c.isascii() for c in v):
        #     raise RequestValidationError("Пароль может содержать только английские буквы")

        # rules = [
        #     any(c.isupper() for c in v),  # хотя бы одна заглавная буква
        #     any(c.islower() for c in v),  # хотя бы одна строчная буква
        #     any(c.isdigit() for c in v),  # хотя бы одна цифра
        #     any(not c.isalnum() for c in v)  # хотя бы один спецсимвол
        # ]

        # if sum(rules) < 2:
        #     raise RequestValidationError("Password must meet at least 2 of the following requirements: uppercase letters, lowercase letters, numbers, special characters")

        return v


class BaseUserResponse(BaseModel):
    id: int
    phone: str


class CreateUser(BaseUserRequest):
    pass


class CreateUserResponse(BaseUserResponse):
    pass


class LoginUserRequest(BaseUserRequest):
    pass


class UserAddressModel(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    address: Optional[str] = None
    entrance: Optional[str] = None
    floor: Optional[int] = None
    apartment: Optional[str] = None
    is_primary: Optional[bool] = None
    is_removed: Optional[bool] = None

class RestaurantModel(BaseModel):
    id: Optional[int] = None
    city_id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    has_delivery: Optional[bool] = None
    has_takeaway: Optional[bool] = None
    has_dine_in: Optional[bool] = None
    is_active: Optional[bool] = None

class CityModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LoginUserResponse(BaseUserResponse):
    last_order_user_address: Optional[UserAddressModel] = None
    last_order_restaurant: Optional[RestaurantModel] = None
    last_order_city: Optional[CityModel] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: Optional[str] = None


class UserLogInDTO(BaseModel):
    user_id: int
    phone: str

class LogInDTO(BaseModel):
    user: UserLogInDTO
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None


class UpdateUserResponse(BaseUserResponse):
    pass

# class TokenData(BaseModel):
#     username: Optional[str] = None


class LogOutResponse(BaseModel):
    message: str
    tokens_revoked: int


class CurrentUserDTO(BaseModel):
    id: int
    phone: str
