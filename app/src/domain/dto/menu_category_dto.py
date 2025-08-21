from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PromotionItem(BaseModel):
    url: str
    description: str


class CategoryItem(BaseModel):
    id: int
    name: str
    # need_addings: Optional[bool] = None


class AddingItem(BaseModel):
    id: int
    name: str
    image_url: str
    price: float


class SizeInfo(BaseModel):
    measure_value: int
    price: float
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
class AddCategoryToRestaurantRequest(BaseModel):
    restaurant_id: int
    category_id: int

    @field_validator("restaurant_id")
    def check_restaurant_id(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Restaurant id must be greater than 0")
        return value

    @field_validator("category_id")
    def check_category_id(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Category id must be greater than 0")
        return value


# Add category

class AddMenuCategoryRequest(BaseModel):
    name: str

    @field_validator("name")
    def check_name(cls, v: str) -> str:
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise ValueError("Invalid characters in name")
        if len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        if len(v) < 3:
            raise ValueError("Category name must be at least 3 characters long")
        return v


class AddMenuCategoryResponse(BaseModel):
    id: int
    name: str
    display_order: int
