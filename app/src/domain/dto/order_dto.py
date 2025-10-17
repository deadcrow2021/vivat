from datetime import datetime
from enum import Enum
import re
from typing import Dict, List, Optional, TypedDict

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
    IN_DELIVERY = "in_delivery"
    DONE = "done"
    CANCELLED = "cancelled"


class IngredientModel(BaseModel):
    name: str
    price: Optional[int] = None
    quantity: Optional[int] = None


class OrderItemModel(BaseModel):
    name: str # полное имя с характеристиками
    quantity: int
    price: int # цена позиции вместе с игредиентами * amount
    add: List[IngredientModel]
    remove: List[IngredientModel]


class OrderModel(BaseModel):
    order_items: List[OrderItemModel]
    status: OrderStatus
    delivery_address: Optional[str] = None
    positions_quantity: int
    order_date: str
    total_price: int
    restaurant_phone: str


class GetOrderResponse(BaseModel):
    orders: List[OrderModel]


class OrderedPosition(BaseModel):
    name: str = Field(..., max_length=500) # Проверить id of FoodVariant соответствует имени
    price: int = Field(..., ge=0) # цена за 1 штуку, но буду сам считать на бэке (в localstorage могут поменять цены)
    quantity: int
    size: int # FoodVariant id
    addings: Optional[Dict[int, int]] = None # {id: amount} of Adding
    removed_ingredients: Optional[List[int]] = None # id of Ingredients

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
        if isinstance(v, dict):
            for item_id, amount in v.items():
                if item_id < 1 or amount < 1:
                    raise RequestValidationError('Id и количество добавок должны быть больше 0')
                if amount > 10:
                    raise RequestValidationError('Количество добавок не может быть больше 9')
        else:
            raise RequestValidationError('Добавки должны быть словарем {id: amount}')
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
    user_info: Optional[UserInfo] = None
    order_quantity: int
    cook_start: str # "13:37"(сейчас) "09:00" "18:30" сиводня
    comment: Optional[str] = Field(max_length=500)
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
        if v == 'asap':
            return v
        if not re.match(r'^([01]\d|2[0-3]):[0-5]\d$', v):
            raise RequestValidationError('Начало готовки должен быть в формате HH:MM')
        return v

    @field_validator('payment_method')
    def validate_payment_method(cls, v):
        # Проверяем допустимые методы оплаты
        if v not in ['cash', 'card']:
            raise RequestValidationError('Метод оплаты должен быть "cash" или "card"')
        return v


class AddIngredient(TypedDict):
    quantity: int
    price: float

class Ingredients(TypedDict):
    add: Dict[str, AddIngredient]
    remove: List[str]

class FoodModel(TypedDict):
    measure_name: str
    measure_value: int
    price: int
    modifier: float
    quantity: int
    ingredients: Ingredients


class CreateOrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    address_id: int
    order_action: OrderAction
    status: OrderStatus
    total_price: int
    unique_code : str
