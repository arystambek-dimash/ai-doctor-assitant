from dataclasses import dataclass
from typing import Optional

from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateSpecializationDTO(BaseDTOMixin):
    title: str
    description: str


@dataclass
class UpdateSpecializationDTO(BaseDTOMixin):
    title: Optional[str] = None
    description: Optional[str] = None