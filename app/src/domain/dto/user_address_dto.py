from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BaseUserAddressRequest(BaseModel):
    address: Optional[str] = None
    entrance: Optional[str] = None
    floor: Optional[float] = None
    apartment: Optional[str] = None
    is_primary: Optional[bool] = None

    @field_validator("address")
    def address_validator(cls, v):
        txt_len = len(v.strip())
        if txt_len < 1 or txt_len > 1000:
            raise ValueError("Address must be between 1 and 1000 characters")
        return v

    @field_validator("entrance")
    def entrance_validator(cls, v):
        txt_len = len(v.strip())
        if txt_len < 1 or txt_len > 20:
            raise ValueError("Entrance must be between 1 and 20 characters")
        return v

    @field_validator("floor")
    def floor_must_be_positive(cls, v):
        if v < 0 or v > 500:
            raise ValueError("Floor must be positive")
        return v

    @field_validator("apartment")
    def entrance_validator(cls, v):
        txt_len = len(v.strip())
        if txt_len < 1 or txt_len > 20:
            raise ValueError("Apartment must be between 1 and 1000 characters")
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

class GetUserAddressResponse(BaseModel):
    addresses: List[GetUserAddress]

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
    pass

class UpdateUserAddressResponse(BaseUserAddressResponse):
    pass

# Delete address

class DeleteAddressResponse(BaseModel):
    id: int
