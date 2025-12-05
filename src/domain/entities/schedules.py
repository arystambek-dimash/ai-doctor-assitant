from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class ScheduleEntity:
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration_minutes: int
    is_active: bool
    doctor_id: int


@dataclass(frozen=True)
class ScheduleWithDoctorEntity:
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration_minutes: int
    is_active: bool
    doctor_id: int
    doctor_name: str
    specialization_name: str


@dataclass(frozen=True)
class TimeSlotEntity:
    start_time: time
    end_time: time
    is_available: bool