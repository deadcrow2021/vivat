from typing import List, Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator


class BaseUserAddressRequest(BaseModel):
    address: Optional[str] = None
    entrance: Optional[str] = None
    floor: Optional[float] = None
    apartment: Optional[str] = None

    @field_validator("address")
    def address_validator(cls, v):
        txt_len = len(v.strip())
        if txt_len < 1 or txt_len > 1000:
            raise RequestValidationError("Адрес должен быть между 1 и 1000 символами")
        return v

    @field_validator("entrance")
    def entrance_validator(cls, v):
        txt_len = len(v.strip())
        if txt_len < 1 or txt_len > 20:
            raise RequestValidationError("Подъезд должен быть между 1 и 20 символами")
        return v

    @field_validator("floor")
    def floor_must_be_positive(cls, v):
        if v < 0 or v > 500:
            raise RequestValidationError("Этаж должен быть положительным числом")
        return v

    @field_validator("apartment")
    def entrance_validator(cls, v):
        txt_len = len(v.strip())
        if txt_len < 1 or txt_len > 20:
            raise RequestValidationError("Квартира должна быть между 1 и 20 символами")
        return v


class BaseUserAddressResponse(BaseModel):
    id: int
    address: str
    entrance: str
    floor: int
    apartment: str
    is_primary: bool


# Get address
class GetUserAddress(BaseUserAddressResponse):
    pass


# Add address

class AddUserAddressRequest(BaseUserAddressRequest):
    address: str
    entrance: str
    floor: float
    apartment: str

class AddUserAddressResponse(BaseUserAddressResponse):
    pass

# Update

class UpdateUserAddressRequest(BaseUserAddressRequest):
    is_primary: Optional[bool] = None

class UpdateUserAddressResponse(BaseUserAddressResponse):
    pass

# Delete address

class DeleteAddressResponse(BaseModel):
    id: int
