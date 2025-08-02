from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

class BaseFeatureRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    icon_url: Optional[str] = Field(None, max_length=2000)

    @field_validator("name", "icon_url")
    def validate_name(cls, v: Optional[str]):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise ValueError("Invalid characters in name")
        if len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        return v

class BaseFeatureResponse(BaseModel):
    id: int
    name: str
    icon_url: str


# Get feature

class GetFeatureResponse(BaseFeatureResponse):
    pass

# Get all features

class GetAllFeaturesResponse(BaseModel):
    data: List[BaseFeatureResponse]


# Create feature

class CreateFeatureRequest(BaseFeatureRequest):
    name: str = Field(..., max_length=100)
    icon_url: str = Field(..., max_length=2000)

class CreateFeatureResponse(BaseFeatureResponse):
    pass


# Delete feature

class DeleteFeatureResponse(BaseModel):
    id: int
