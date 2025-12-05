from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.constants import AppointmentStatus


@dataclass(frozen=True)
class AppointmentEntity:
    id: int
    date_time: datetime
    status: AppointmentStatus
    notes: Optional[str]
    patient_id: int
    doctor_id: int
    ai_consultation_id: Optional[int]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AppointmentWithDetailsEntity:
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