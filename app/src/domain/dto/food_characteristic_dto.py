from typing import List, Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator


class AddCharacteristicsToVariantRequest(BaseModel):
    variant_id: int
    characteristic_value: str = Field(..., max_length=200)

    @field_validator("variant_id")
    def validate_longitude(cls, v: Optional[int]):
        if v is None:
            return v
        if v < 1:
            raise RequestValidationError("Id варианта блюда не может быть меньше 1")
        return v

    @field_validator("characteristic_value")
    def validate_name(cls, v: Optional[str]):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Недопустимые символы в значении характеристики")
        if len(v.strip()) == 0:
            raise RequestValidationError("Значение характеристики не может быть пустым")
        return v


class AddCharacteristicsToVariantResponse(BaseModel):
    id: int
    measure_value: str
