from typing import List, Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator


class PromotionItem(BaseModel):
    url: str
    description: str


class CategoryItem(BaseModel):
    id: int
    name: str
    need_addings: bool


class AddingItem(BaseModel):
    id: int
    name: str
    image_url: str
    price: int


class SizeInfo(BaseModel):
    measure_value: int
    price: int
    price_multiplier: Optional[float]


class PositionItem(BaseModel):
    id: int
    name: str
    image_url: str
    description: str
    measure_name: str
    size: Optional[List[SizeInfo]] = None
    ingredients: Optional[List[AddingItem]] = None


class HomeData(BaseModel):
    promotions: Optional[List[PromotionItem]] = None
    categories: List[CategoryItem]
    positions: Optional[List[PositionItem]] = None


class HomePageResponse(BaseModel):
    date: Optional[HomeData] = None


### Add categoty to restaurant
class AddCategoryToRestaurantRequest(BaseModel): # TODO: добавить эндпоинт по добавлению категории к ресторану
    restaurant_id: int
    category_id: int

    @field_validator("restaurant_id")
    def check_restaurant_id(cls, value: int) -> int:
        if value < 1:
            raise RequestValidationError("Id ресторана не может быть меньше 1")
        return value

    @field_validator("category_id")
    def check_category_id(cls, value: int) -> int:
        if value < 1:
            raise RequestValidationError("Id категории не может быть меньше 1")
        return value


# Add category

class AddMenuCategoryRequest(BaseModel):
    name: str

    @field_validator("name")
    def check_name(cls, v: str) -> str:
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Недопустимые символы в имени")
        if len(v.strip()) == 0:
            raise RequestValidationError("Имя не может быть пустым")
        return v


class AddMenuCategoryResponse(BaseModel):
    id: int
    name: str
    display_order: int
