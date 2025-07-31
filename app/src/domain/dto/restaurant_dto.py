from enum import Enum
import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator


class RestaurantActionEnum(Enum):
    DELIVERY = "delivery"
    TAKEAWAY = "takeaway"
    INSIDE = "inside"


class BaseRestaurantRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = None
    address: Optional[str] = Field(None, max_length=5000)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    has_delivery: Optional[bool] = None
    has_takeaway: Optional[bool] = None
    has_dine_in: Optional[bool] = None
    is_active: Optional[bool] = None

    @field_validator("name")
    def validate_name(cls, v: Optional[str]):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise ValueError("Invalid characters in name")
        if len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("phone")
    def validate_phone(cls, v: Optional[str]):
        if v is None:
            return v
        pattern = r"^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid Russian phone number format")
        return v

    @field_validator("address")
    def validate_address(cls, v: Optional[str]):
        if v is None:
            return v
        if len(v.strip()) == 0:
            raise ValueError("Address cannot be empty")
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


class BaseRestaurantResponse(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    coords: Optional[List[float]] = None
    actions: Optional[List[RestaurantActionEnum]] = None
    is_active: Optional[bool] = None


### GET RESTAURANTS

class DayShortName(str, Enum):
    MONDAY = "пн"
    TUESDAY = "вт"
    WEDNESDAY = "ср"
    THURSDAY = "чт"
    FRIDAY = "пт"
    SATURDAY = "сб"
    SUNDAY = "вс"


class HoursItem(BaseModel):
    from_: str
    to: str

    class Config:
        allow_population_by_field_name = True


class WorkingHoursModel(RootModel):
    root: Dict[DayShortName, HoursItem]


class RestaurantItem(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    coords: List[float]
    working_hours: WorkingHoursModel
    features: List[str]
    actions: List[RestaurantActionEnum]


class RestaurantData(BaseModel):
    restaurants: List[RestaurantItem]
    center_coords: List[float]


class GetCityRestaurantsResponse(BaseModel):
    data: Optional[RestaurantData] = None

    class Config:
        exclude_none = True


class GetRestaurantResponse(RestaurantItem):
    pass


### ADD RESTAURANT

class AddRestaurantRequest(BaseRestaurantRequest):
    name: str = Field(..., max_length=500)
    phone: str = Field(...)
    address: str = Field(..., max_length=5000)
    latitude: float = Field(...)
    longitude: float = Field(...)
    has_delivery: bool = Field(...)
    has_takeaway: bool = Field(...)
    has_dine_in: bool = Field(...)
    is_active: bool = Field(True)


class AddRestaurantResponse(BaseRestaurantResponse):
    pass


# Update restaurant

class UpdateRestaurantRequest(BaseRestaurantRequest):
    pass

class UpdateRestaurantResponse(BaseRestaurantResponse):
    pass


# Delete restaurant


class DeleteRestaurantResponse(BaseModel):
    id: int
    message: str
