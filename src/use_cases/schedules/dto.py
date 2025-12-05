from dataclasses import dataclass
from datetime import time
from typing import Optional

from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateScheduleDTO(BaseDTOMixin):
    day_of_week: int
    start_time: time
    end_time: time
    doctor_id: int
    slot_duration_minutes: int = 30
    is_active: bool = True


@dataclass
class UpdateScheduleDTO(BaseDTOMixin):
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None