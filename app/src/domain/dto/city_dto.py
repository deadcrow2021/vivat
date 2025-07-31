from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BaseCityRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("name")
    def validate_name(cls, v: Optional[str]):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise ValueError("Invalid characters in name")
        if len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("latitude")
    def validate_latitude(cls, v: Optional[float]):
        if v is None:
            return v
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v: Optional[float]):
        if v is None:
            return v
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class BaseCityResponse(BaseModel):
    id: int
    name: str
    coordiantes: List[float]


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
