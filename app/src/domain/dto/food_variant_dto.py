from pydantic import BaseModel


class BaseCityResponse(BaseModel):
    id: int
    food_id: int
    price: int
    ingredient_price_modifier: float
    is_active: bool


class FoodVariantResponse(BaseCityResponse):
    pass
