from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PromotionItem(BaseModel):
    url: str
    description: str


class CategoryItem(BaseModel):
    id: int
    name: str
    need_addings: Optional[bool] = None


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
