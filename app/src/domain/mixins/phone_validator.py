from typing import Optional
import re

from pydantic import field_validator
import phonenumbers


class PhoneValidatorMixin:
    """Миксин с валидацией и нормализацией телефонных номеров"""
    
    @field_validator("phone")
    @classmethod
    def validate_and_normalize_phone(cls, v: str) -> str:
        try:
            phone_obj = phonenumbers.parse(v, "RU")
        except phonenumbers.NumberParseException:
            raise ValueError("Некорректный номер телефона")

        if not phonenumbers.is_valid_number(phone_obj):
            raise ValueError("Невалидный номер телефона")

        # нормализуем к E.164 (+7XXXXXXXXXX)
        return phonenumbers.format_number(
            phone_obj, phonenumbers.PhoneNumberFormat.E164
        )
