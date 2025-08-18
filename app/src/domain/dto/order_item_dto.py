from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AddOrderItemRequest(BaseModel):
    food_id: int
    order_id: int
    final_price: float

    @field_validator("food_id")
    def validate_food_id(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise ValueError("Food id must be greater than 0")
        return v

    @field_validator("order_id")
    def validate_order_id(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise ValueError("Order id must be greater than 0")
        return v

    @field_validator("final_price")
    def validate_total_price(cls, v: float):
        if v < 0:
            raise ValueError("Total price must be greater than 0")
        return v

class AddOrderItemResponse(BaseModel):
    id: int
    food_id: int
    order_id: int
    final_price: float
