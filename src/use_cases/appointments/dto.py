from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.constants import AppointmentStatus
from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateAppointmentDTO(BaseDTOMixin):
    date_time: datetime
    patient_id: int
    doctor_id: int
    notes: Optional[str] = None
    ai_consultation_id: Optional[int] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED


@dataclass
class UpdateAppointmentDTO(BaseDTOMixin):
    date_time: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None