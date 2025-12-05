from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.constants import DoctorStatus


@dataclass(frozen=True)
class DoctorEntity:
    id: int
    bio: str
    rating: float
    experience_years: int
    license_number: str
    status: DoctorStatus
    rejection_reason: Optional[str]
    user_id: int
    specialization_id: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class DoctorWithDetailsEntity:
    id: int
    bio: str
    rating: float
    experience_years: int
    license_number: str
    status: DoctorStatus
    rejection_reason: Optional[str]
    user_id: int
    specialization_id: int
    created_at: datetime
    updated_at: datetime
    full_name: str
    email: str
    phone: Optional[str]
    specialization_name: str
