from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.constants import AppointmentStatus, VisitType


@dataclass(frozen=True)
class AppointmentEntity:
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


@dataclass(frozen=True)
class AppointmentWithDetailsEntity:
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
