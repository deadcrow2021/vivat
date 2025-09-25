from datetime import datetime
from typing import List, Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator


class AddOrderItemRequest(BaseModel):
    food_variant_id: int
    order_id: int
    final_price: int

    @field_validator("food_variant_id")
    def validate_food_id(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise RequestValidationError("Id блюда должен быть больше 0")
        return v

    @field_validator("order_id")
    def validate_order_id(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise RequestValidationError("Id заказа должен быть больше 0")
        return v

    @field_validator("final_price")
    def validate_total_price(cls, v: float):
        if v < 0:
            raise RequestValidationError("Итоговая цена должна быть больше 0")
        return v

class AddOrderItemResponse(BaseModel):
    id: int
    food_id: int
    order_id: int
    final_price: int
