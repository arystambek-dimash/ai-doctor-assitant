from datetime import time, date

from pydantic import BaseModel


class ScheduleResponse(BaseModel):
    id: int
    day_of_week: int
    day_name: str
    start_time: time
    end_time: time
    slot_duration_minutes: int
    is_active: bool
    doctor_id: int

    @classmethod
    def from_entity(cls, entity) -> "ScheduleResponse":
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return cls(
            id=entity.id,
            day_of_week=entity.day_of_week,
            day_name=days[entity.day_of_week],
            start_time=entity.start_time,
            end_time=entity.end_time,
            slot_duration_minutes=entity.slot_duration_minutes,
            is_active=entity.is_active,
            doctor_id=entity.doctor_id,
        )


class TimeSlotResponse(BaseModel):
    start_time: time
    end_time: time
    is_available: bool

    class Config:
        from_attributes = True


class AvailableSlotsRequest(BaseModel):
    date: date

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-12-20"
            }
        }
