from datetime import datetime
from enum import Enum
import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator


class RestaurantActionEnum(Enum):
    DELIVERY = "delivery"
    TAKEAWAY = "takeaway"
    INSIDE = "inside"

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
    is_holiday: bool


class WorkingHoursModel(RootModel):
    root: Dict[DayShortName, HoursItem]


class BaseRestaurantRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
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
    is_active: Optional[bool] = None
    actions: Optional[List[RestaurantActionEnum]] = None
    working_hours: WorkingHoursModel
    menu_categories: List[int]
    features: List[str]


### GET RESTAURANTS

    class Config:
        allow_population_by_field_name = True


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
    working_hours: Optional[WorkingHoursModel] = None
    menu_categories: Optional[List[int]] = None
    features: Optional[List[str]] = None
    
    @field_validator("working_hours")
    def validate_working_hours(cls, v: Optional[WorkingHoursModel]):
        if v is None:
            return v
        
        for day, hours in v.root.items():
            try:
                opens = datetime.strptime(hours.from_, "%H:%M").time()
                closes = datetime.strptime(hours.to, "%H:%M").time()
                if opens >= closes:
                    raise ValueError(f"Opening time must be before closing time for {day}")
            except ValueError as e:
                raise ValueError(f"Invalid time format for {day}: {str(e)}")
        
        return v

    @field_validator("features")
    def validate_features(cls, v: Optional[List[str]]):
        if v is None:
            return v
        
        if len(v) != len(set(v)):
            raise ValueError("Feature names must be unique")
        
        for feature in v:
            if not feature.strip():
                raise ValueError("Feature name cannot be empty")
            if len(feature) > 100:
                raise ValueError("Feature name is too long (max 100 chars)")
            if any(char in feature for char in ["'", '"', ";", "--"]):
                raise ValueError("Invalid characters in feature name")
        
        return v

class UpdateRestaurantResponse(BaseRestaurantResponse):
    pass


# Delete restaurant


class DeleteRestaurantResponse(BaseModel):
    id: int
    message: str
