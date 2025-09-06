from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.domain.mixins.phone_validator import PhoneValidatorMixin


class BaseUserResponse(PhoneValidatorMixin, BaseModel):
    id: int
    name: str
    phone: str
    email: str


class GetUserResponse(BaseUserResponse):
    pass
