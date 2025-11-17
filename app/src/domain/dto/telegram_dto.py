from typing import Dict, List, Optional, TypedDict

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator

from src.domain.enums.enums import OrderAction


class SendOrderInfo(BaseModel):
    restaurant_id: int
    order_id: int
    message_text: str
    current_status: str
    action: OrderAction


class UpdateOrderInfo(BaseModel):
    chat_id: int
    message_id: int
    order_id: int
    message_text: str
    current_status: str
    action: OrderAction


class TelegramResponse(BaseModel):
    message: str
