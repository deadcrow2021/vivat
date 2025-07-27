from enum import Enum
import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator


# Get City
class GetCityResponse(BaseModel):
    name: str
    coordiantes: List[float]
