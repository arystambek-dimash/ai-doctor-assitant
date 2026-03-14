from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.constants import AppointmentStatus, VisitType
from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateAppointmentDTO(BaseDTOMixin):
    date_time: datetime
    patient_id: int
    doctor_id: int
    duration_minutes: int = 30
    visit_type: VisitType = VisitType.OFFLINE
    notes: Optional[str] = None
    triage_run_id: Optional[int] = None
    rescheduled_from_id: Optional[int] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED


@dataclass
class UpdateAppointmentDTO(BaseDTOMixin):
    date_time: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    duration_minutes: Optional[int] = None
    visit_type: Optional[VisitType] = None
    notes: Optional[str] = None
    cancel_reason: Optional[str] = None
