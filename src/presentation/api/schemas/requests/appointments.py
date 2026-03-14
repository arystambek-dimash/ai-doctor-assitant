from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.constants import AppointmentStatus, VisitType


class AppointmentCreateRequest(BaseModel):
    date_time: datetime
    doctor_id: int
    duration_minutes: int = Field(30, ge=15, le=120)
    visit_type: VisitType = VisitType.OFFLINE
    notes: Optional[str] = Field(None, max_length=2000)
    triage_run_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "date_time": "2024-12-20T10:00:00",
                "doctor_id": 1,
                "duration_minutes": 30,
                "visit_type": "offline",
                "notes": "Follow-up consultation"
            }
        }


class AdminAppointmentCreateRequest(BaseModel):
    """Request schema for admin to create appointments for any patient."""
    date_time: datetime
    doctor_id: int
    patient_id: int
    duration_minutes: int = Field(30, ge=15, le=120)
    visit_type: VisitType = VisitType.OFFLINE
    notes: Optional[str] = Field(None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "date_time": "2024-12-20T10:00:00",
                "doctor_id": 1,
                "patient_id": 2,
                "duration_minutes": 30,
                "visit_type": "offline",
                "notes": "Follow-up consultation"
            }
        }


class AppointmentUpdateRequest(BaseModel):
    date_time: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=120)
    visit_type: Optional[VisitType] = None
    notes: Optional[str] = Field(None, max_length=2000)
    cancel_reason: Optional[str] = Field(None, max_length=500)
