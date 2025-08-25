from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BaseUserAddressRequest(BaseModel):
    address: Optional[str] = None
    entrance: Optional[str] = None
    floor: Optional[float] = None
    apartment: Optional[str] = None
    is_primary: Optional[bool] = None # TODO: Add logic for is_primary
    
    # TODO: Add validators

    @field_validator("address")
    def address_must_not_be_empty(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Address cannot be empty")
        return v
    
    @field_validator("floor")
    def floor_must_be_positive(cls, v):
        if v < 0 or v > 500:
            raise ValueError("Floor must be positive")
        return v


class AddUserAddressResponse(BaseModel):
    address: str
    entrance: str
    floor: int
    apartment: str
    is_primary: bool


# Add address

class AddUserAddressRequest(BaseUserAddressRequest):
    pass