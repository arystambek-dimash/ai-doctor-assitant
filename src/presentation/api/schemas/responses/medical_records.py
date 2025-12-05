from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MedicalRecordResponse(BaseModel):
    id: int
    diagnosis: str
    prescription: Optional[str]
    notes: Optional[str]
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordWithDetailsResponse(BaseModel):
    id: int
    diagnosis: str
    prescription: Optional[str]
    notes: Optional[str]
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    patient_name: str
    patient_email: str
    doctor_name: str
    specialization_name: str

    class Config:
        from_attributes = True
