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
            raise RequestValidationError("Название не может превышать 500 символов")
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Недопустимые символы в названии")
        if len(v.strip()) == 0:
            raise RequestValidationError("Название не может быть пустым")
        return v
    
    @field_validator("image_url")
    def validate_file_path(cls, v: str):
        # Проверяем, что строка содержит хотя бы один разделитель пути (/ или \)
        if not any(separator in v for separator in ("/", "\\")):
            raise RequestValidationError("Недопустимый формат пути к файлу - должен содержать / или \\")

        # Проверяем отсутствие опасных символов
        if any(char in v for char in ["<", ">", ":", "|", "?", "*", "'", '"', ";", "--"]):
            raise RequestValidationError("Недопустимые символы в пути к файлу")
        return v
    
    @field_validator("description")
    def validate_description(cls, v: str):
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Недопустимые символы в описании")
        if len(v) > 5000:
            raise RequestValidationError("Описание не может превышать 5000 символов")
        return v

    @field_validator("measure_name")
    def validate_measure_name(cls, v: str):
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise RequestValidationError("Недопустимые символы в названии меры измерения")
        if len(v) > 50:
            raise RequestValidationError("Название меры измерения не может превышать 50 символов")
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
