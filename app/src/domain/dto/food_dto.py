from typing import List, Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator


class BaseFoodRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=2000)
    description: Optional[str] = Field(None, max_length=5000)
    measure_name: Optional[str] = Field(None, max_length=50)

    @field_validator("name")
    def validate_name(cls, v: Optional[str]):
        if v is None:
            return v
        if len(v) > 500:
            raise RequestValidationError("Measure name exceeds maximum length of 50 characters")
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Invalid characters in name")
        if len(v.strip()) == 0:
            raise RequestValidationError("Name cannot be empty")
        return v
    
    @field_validator("image_url")
    def validate_file_path(cls, v: str):
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Invalid characters in name")
        # Проверяем, что строка содержит хотя бы один разделитель пути (/ или \)
        if not any(separator in v for separator in ("/", "\\")):
            raise RequestValidationError("Invalid file path format - must contain / or \\")

        # Проверяем отсутствие опасных символов
        if any(char in v for char in ["<", ">", ":", "|", "?", "*"]):
            raise RequestValidationError("Invalid characters in file path")
        return v
    
    @field_validator("description")
    def validate_description(cls, v: str):
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Invalid characters in name")
        if len(v) > 5000:
            raise RequestValidationError("Description exceeds maximum length of 5000 characters")
        return v

    @field_validator("measure_name")
    def validate_measure_name(cls, v: str):
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Invalid characters in name")
        if len(v) > 50:
            raise RequestValidationError("Measure name exceeds maximum length of 50 characters")
        return v


class BaseFoodResponse(BaseModel):
    id: int
    category_id: int
    name: str
    image_url: str
    description: str
    measure_name: str


# Get food

class GetFoodResponse(BaseFoodResponse):
    pass


# Add food

class AddFoodRequest(BaseFoodRequest):
    name: str = Field(..., max_length=500)
    image_url: Optional[str] = Field(None, max_length=2000)
    description: Optional[str] = Field(None, max_length=5000)
    measure_name: Optional[str] = Field(None, max_length=50)

class AddFoodResponse(BaseFoodResponse):
    pass
