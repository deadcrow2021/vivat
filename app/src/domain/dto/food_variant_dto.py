from typing import List, Optional
from pydantic import BaseModel


class BaseCityResponse(BaseModel):
    id: int
    food_id: int
    price: int
    ingredient_price_modifier: float
    is_active: bool


class FoodVariantResponse(BaseCityResponse):
    pass


class IngredientItem(BaseModel):
    id: int
    name: str
    image_url: str
    price: int


class SizeInfo(BaseModel):
    id: int
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
    ingredients: Optional[List[IngredientItem]] = None


class PositionsResponse(BaseModel):
    positions: Optional[List[PositionItem]]
