import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BaseUserRequest(BaseModel):
    phone: str = Field(..., max_length=20)
    password: str = Field(..., min_length=8, max_length=16)

    @field_validator("password")
    def validate_password(cls, v: str):
        if len(v) < 8 or len(v) > 16:
            raise ValueError("Password must be between 8 and 16 characters")

        rules = [
            any(c.isupper() for c in v),  # хотя бы одна заглавная буква
            any(c.islower() for c in v),  # хотя бы одна строчная буква
            any(c.isdigit() for c in v),  # хотя бы одна цифра
            any(not c.isalnum() for c in v)  # хотя бы один спецсимвол
        ]

        if sum(rules) < 2:
            raise ValueError("Password must meet at least 2 of the following requirements: uppercase letters, lowercase letters, numbers, special characters")
        
        return v

    @field_validator("phone")
    def validate_phone(cls, v: Optional[str]):
        if v is None:
            return v
        pattern = r"^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid Russian phone number format")
        return v


class BaseUserResponse(BaseModel):
    id: int
    phone: str
    # email: str


class CreateUser(BaseUserRequest):
    pass
    # email: str = Field(..., max_length=100)

    # @field_validator("email")
    # def validate_email(cls, v: Optional[str]):
    #     if v is None:
    #         return v
    #     pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    #     if not re.match(pattern, v):
    #         raise ValueError("Invalid email format")
    #     return v


class CreateUserResponse(BaseUserResponse):
    pass


class LoginUserRequest(BaseUserRequest):
    pass

class LoginUserResponse(BaseUserResponse):
    pass


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
