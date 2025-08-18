from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AddUserAddressRequest(BaseModel):
    address: str
    entrance: str
    floor: int
    apartment: str
    is_primary: bool # TODO: Add logic for is_primary
    
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
