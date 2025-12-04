from dataclasses import dataclass
from typing import Optional

from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateUserDTO(BaseDTOMixin):
    email: str
    password_hash: str
    full_name: str
    phone: str
    is_admin: bool


@dataclass
class UpdateUserDTO(CreateUserDTO):
    email: Optional[str] = None
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_admin: Optional[bool] = None