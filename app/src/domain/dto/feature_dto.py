from typing import List, Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator


class BaseFeatureRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    icon_url: Optional[str] = Field(None, max_length=2000)

    @field_validator("name", "icon_url")
    def validate_name(cls, v: Optional[str]):
        if v is None:
            return v
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Invalid characters in name")
        if len(v.strip()) == 0:
            raise RequestValidationError("Name cannot be empty")
        return v

    @field_validator("icon_url")
    def validate_file_path(cls, v: str):
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Invalid characters in url")
        # Проверяем, что строка содержит хотя бы один разделитель пути (/ или \)
        if not any(separator in v for separator in ("/", "\\")):
            raise RequestValidationError("Invalid file path format - must contain / or \\")
        
        # Проверяем отсутствие опасных символов
        if any(char in v for char in ["<", ">", ":", "|", "?", "*"]):
            raise RequestValidationError("Invalid characters in file path")
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
