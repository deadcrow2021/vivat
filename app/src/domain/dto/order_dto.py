from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class OrderRequest(BaseModel):
    user_id: int
    restaurant_id: int
    address_id: int
    total_price: float
    status: str

    @field_validator("user_id")
    def validate_latitude(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise ValueError("User id must be greater than 0")
        return v
    
    @field_validator("restaurant_id")
    def validate_restaurant_id(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise ValueError("Restaurant id must be greater than 0")
        return v
    
    @field_validator("address_id")
    def validate_address_id(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise ValueError("Address id must be greater than 0")
        return v
    
    @field_validator("total_price")
    def validate_total_price(cls, v: float):
        if v < 0:
            raise ValueError("Total price must be greater than 0")
        return v
    
    @field_validator("status")
    def validate_status(cls, v: str):
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise ValueError("Invalid characters in name")
        if len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        if not v.isalpha():
            raise ValueError("Status must be a string")
        return v
    
class OrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    address_id: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime
