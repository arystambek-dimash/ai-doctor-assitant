from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.constants import AppointmentStatus


class AppointmentCreateRequest(BaseModel):
    date_time: datetime
    doctor_id: int
    notes: Optional[str] = Field(None, max_length=2000)
    ai_consultation_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "date_time": "2024-12-20T10:00:00",
                "doctor_id": 1,
                "notes": "Follow-up consultation"
            }
        }


class AppointmentUpdateRequest(BaseModel):
    date_time: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)
