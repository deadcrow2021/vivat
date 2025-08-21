from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

class BaseFoodRequest(BaseModel):
    name: str
    image_url: str
    description: str
    measure_name: str


class BaseFoodResponse(BaseModel):
    id: int
    category_id: int
    name: str
    image_url: str
    description: str
    measure_name: str


# Add food

class AddFoodRequest(BaseFoodRequest):
    pass

class AddFoodResponse(BaseFoodResponse):
    pass
