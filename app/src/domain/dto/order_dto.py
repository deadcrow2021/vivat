from datetime import datetime
from decimal import Decimal
from enum import Enum
import re
from typing import List, Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator

from src.domain.mixins.phone_validator import PhoneValidatorMixin


class OrderAction(Enum):
    UNKNOWN = "unknown"
    DELIVERY = "delivery"
    TAKEAWAY = "takeaway"
    INSIDE = "inside"

class OrderStatus(Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class OrderedPosition(BaseModel):
    name: str = Field(..., max_length=500) # Проверить id of FoodVariant соответствует имени
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2) # цена за 1 штуку, но буду сам считать на бэке (в localstorage могут поменять цены)
    quantity: int
    size: int # id of FoodVariant
    addings: Optional[List[int]] = None # id of Adding
    removed_ingredients: Optional[List[int]] = None

    @field_validator("name")
    def validate_name(cls, v: str):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Invalid characters in name")
        if len(v.strip()) == 0:
            raise RequestValidationError("Name cannot be empty")
        return v

    @field_validator("quantity")
    def validate_quantity(cls, v: int):
        if v is None:
            return v
        if v < 1 or v > 19: # TODO: Спросить
            raise RequestValidationError("Quantity must be greater than 0 or lower than 99")
        return v

    @field_validator('addings')
    def validate_addings(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            for item in v:
                if item < 1:
                    raise RequestValidationError('Addings id must be greater than 0')
        else:
            raise RequestValidationError('Addings must be a list')
        return v

    @field_validator('removed_ingredients')
    def validate_removed_ingridients(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            for item in v:
                if item < 1:
                    raise RequestValidationError('Removed ingridients id must be greater than 0')
        else:
            raise RequestValidationError('Removed ingridients must be a list')
        return v


class SelectedRestaurant(PhoneValidatorMixin, BaseModel):
    id: int
    action: OrderAction # проверить есть ли у этого ресторана такой action
    address: str = Field(..., max_length=5000)
    phone: str 
    # проверить адрес и телефон, сравнить с id ресторана

    @field_validator("address")
    def validate_address(cls, v: str):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Invalid characters in address")
        if len(v.strip()) == 0:
            raise RequestValidationError("Address cannot be empty")
        return v


class UserInfo(BaseModel):
    address_id: int # беру пользователя из токена и сравниваю его адрес с адресом в заказе

    @field_validator("address_id")
    def validate_latitude(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise RequestValidationError("Id must be greater than 0 or lower than 99")
        return v

class OrderRequest(BaseModel):
    selected_restaurant: SelectedRestaurant
    order_list: List[OrderedPosition]
    user_info: UserInfo
    order_quantity: int # TODO: Спросить
    cook_start: str # "13:37"(сейчас) "09:00" "18:30" сиводня
    payment_method: str # "cash", "card"

    @field_validator("order_quantity")
    def validate_order_quantity(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1 or v > 99:
            raise RequestValidationError("Order quantity must be greater than 0 or lower than 99")
        return v

    @field_validator("cook_start")
    def validate_cook_start(cls, v):
        # Проверяем формат времени HH:MM
        if not re.match(r'^([01]\d|2[0-3]):[0-5]\d$', v):
            raise RequestValidationError('cook_start должен быть в формате HH:MM')
        return v

    @field_validator('payment_method')
    def validate_payment_method(cls, v):
        # Проверяем допустимые методы оплаты
        if v not in ['cash', 'card']:
            raise RequestValidationError('payment_method должен быть "cash" или "card"')
        return v


class CreateOrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    address_id: int
    order_action: OrderAction
    status: OrderStatus
    total_price: float
    unique_code : str
