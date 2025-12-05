from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.constants import DoctorStatus


class DoctorResponse(BaseModel):
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

    class Config:
        from_attributes = True


class DoctorWithDetailsResponse(BaseModel):
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

    class Config:
        from_attributes = True


class DoctorPublicResponse(BaseModel):
    """Public doctor info (no sensitive data)."""
    id: int
    bio: str
    rating: float
    experience_years: int
    specialization_id: int
    full_name: str
    specialization_name: str

    class Config:
        from_attributes = True


class ApplicationStatusResponse(BaseModel):
    has_application: bool
    status: Optional[str] = None
    rejection_reason: Optional[str] = None
