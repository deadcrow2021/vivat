from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.domain.mixins.phone_validator import PhoneValidatorMixin


class BaseUserResponse(PhoneValidatorMixin, BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class GetUserResponse(BaseUserResponse):
    pass
