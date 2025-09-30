from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from fastapi.exceptions import RequestValidationError


class BaseCityRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("name")
    def validate_name(cls, v: Optional[str]):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Недопустипые символы в названии")
        if len(v.strip()) == 0:
            raise RequestValidationError("Название не может быть пустым")
        return v

    @field_validator("latitude")
    def validate_latitude(cls, v: Optional[float]):
        if v is None:
            return v
        if not (-90 <= v <= 90):
            raise RequestValidationError("Широта должна быть между -90 и 90")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v: Optional[float]):
        if v is None:
            return v
        if not (-180 <= v <= 180):
            raise RequestValidationError("Долгота должна быть между -180 и 180")
        return v


class BaseCityResponse(BaseModel):
    id: int
    name: str
    coordinates: List[float]


# Get City
class GetCityResponse(BaseCityResponse):
    pass


# Get all Cities
class GetAllCitiesResponse(BaseModel):
    data: List[GetCityResponse]


# Add City
class AddCityRequest(BaseCityRequest):
    name: str = Field(..., max_length=100)
    latitude: float = Field(...)
    longitude: float = Field(...)

class AddCityResponse(BaseCityResponse):
    pass


# Update City

class UpdateCityRequest(BaseCityRequest):
    pass

class UpdateCityResponse(BaseCityResponse):
    pass


# Delete restaurant

class DeleteCityResponse(BaseModel):
    id: int
