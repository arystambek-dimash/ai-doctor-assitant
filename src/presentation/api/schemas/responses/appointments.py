from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.constants import AppointmentStatus, VisitType


class AppointmentResponse(BaseModel):
    id: int
    date_time: datetime
    status: AppointmentStatus
    duration_minutes: int
    visit_type: VisitType
    notes: Optional[str]
    cancel_reason: Optional[str]
    patient_id: int
    doctor_id: int
    triage_run_id: Optional[int]
    rescheduled_from_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentWithDetailsResponse(BaseModel):
    id: int
    date_time: datetime
    status: AppointmentStatus
    duration_minutes: int
    visit_type: VisitType
    notes: Optional[str]
    cancel_reason: Optional[str]
    patient_id: int
    doctor_id: int
    triage_run_id: Optional[int]
    rescheduled_from_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    patient_name: str
    patient_phone: Optional[str]
    doctor_name: str
    specialization_name: str

    class Config:
        from_attributes = True


class TimeSlotResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    is_available: bool


class DoctorAvailabilityResponse(BaseModel):
    doctor_id: int
    date: str
    slots: list[TimeSlotResponse]
