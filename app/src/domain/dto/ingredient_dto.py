from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class IngredientResponse(BaseModel):
    id: int
    name: str
    price: int
    image_url: str
