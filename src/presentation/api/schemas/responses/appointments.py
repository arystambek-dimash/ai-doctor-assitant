from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.constants import AppointmentStatus


class AppointmentResponse(BaseModel):
    id: int
    date_time: datetime
    status: AppointmentStatus
    notes: Optional[str]
    patient_id: int
    doctor_id: int
    ai_consultation_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentWithDetailsResponse(BaseModel):
    id: int
    date_time: datetime
    status: AppointmentStatus
    notes: Optional[str]
    patient_id: int
    doctor_id: int
    ai_consultation_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    patient_name: str
    patient_email: str
    patient_phone: Optional[str]
    doctor_name: str
    specialization_name: str

    class Config:
        from_attributes = True
