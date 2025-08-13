from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BaseUserResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str


class GetUserResponse(BaseUserResponse):
    pass
