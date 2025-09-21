from typing import Optional
import re

from pydantic import field_validator


class PhoneValidatorMixin:
    """Миксин с валидацией и нормализацией телефонных номеров"""
    
    @field_validator("phone")
    @classmethod
    def validate_and_normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
            
        pattern = r"^(\+7|7|8)?[\s\-]?\(?([0-9]{3})\)?[\s\-]?([0-9]{3})[\s\-]?([0-9]{2})[\s\-]?([0-9]{2})$"
        match = re.match(pattern, v)
        
        if not match:
            raise ValueError("Невалидный формат Российского номера телефона")
        
        # Нормализуем номер к формату +7XXXXXXXXXX
        groups = match.groups()
        code = groups[1]  # код оператора
        part1 = groups[2]  # первые 3 цифры
        part2 = groups[3]  # следующие 2 цифры
        part3 = groups[4]  # последние 2 цифры
        
        return f"+7{code}{part1}{part2}{part3}"
