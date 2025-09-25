from datetime import datetime
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
    price: int = Field(..., ge=0) # цена за 1 штуку, но буду сам считать на бэке (в localstorage могут поменять цены)
    quantity: int
    size: int # id of FoodVariant
    addings: Optional[List[int]] = None # id of Adding
    removed_ingredients: Optional[List[int]] = None

    @field_validator("name")
    def validate_name(cls, v: str):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Недопустимые символы в имени")
        if len(v.strip()) == 0:
            raise RequestValidationError("Имя не может быть пустым")
        return v

    @field_validator("quantity")
    def validate_quantity(cls, v: int):
        if v is None:
            return v
        if v < 1 or v > 19:
            raise RequestValidationError("Количество блюда должно быть больше 0 или меньше 20")
        return v

    @field_validator('addings')
    def validate_addings(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            for item in v:
                if item < 1:
                    raise RequestValidationError('Id добавок должен быть больше 0')
        else:
            raise RequestValidationError('Добавки должны быть списком')
        return v

    @field_validator('removed_ingredients')
    def validate_removed_ingridients(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            for item in v:
                if item < 1:
                    raise RequestValidationError('Id убираемых ингридиентов должен быть больше 0')
        else:
            raise RequestValidationError('Уибраемые ингридиенты должны быть списком')
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
            raise RequestValidationError("Недопустимые символы в адресе")
        if len(v.strip()) == 0:
            raise RequestValidationError("Адрес не может быть пустым")
        return v


class UserInfo(BaseModel):
    address_id: int # беру пользователя из токена и сравниваю его адрес с адресом в заказе

    @field_validator("address_id")
    def validate_latitude(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise RequestValidationError("Id адреса должен быть больше 0")
        return v

class OrderRequest(BaseModel):
    selected_restaurant: SelectedRestaurant
    order_list: List[OrderedPosition]
    user_info: UserInfo
    order_quantity: int
    cook_start: str # "13:37"(сейчас) "09:00" "18:30" сиводня
    payment_method: str # "cash", "card"

    @field_validator("order_quantity")
    def validate_order_quantity(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1 or v > 99:
            raise RequestValidationError("Количество блюд в заказе должно быть больше 1 и меньше 99")
        return v

    @field_validator("cook_start")
    def validate_cook_start(cls, v):
        # Проверяем формат времени HH:MM
        if not re.match(r'^([01]\d|2[0-3]):[0-5]\d$', v):
            raise RequestValidationError('Начало готовки должен быть в формате HH:MM')
        return v

    @field_validator('payment_method')
    def validate_payment_method(cls, v):
        # Проверяем допустимые методы оплаты
        if v not in ['cash', 'card']:
            raise RequestValidationError('Метод оплаты должен быть "cash" или "card"')
        return v


class CreateOrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    address_id: int
    order_action: OrderAction
    status: OrderStatus
    total_price: int
    unique_code : str
