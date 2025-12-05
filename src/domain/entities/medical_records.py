from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class MedicalRecordEntity:
    id: int
    diagnosis: str
    prescription: Optional[str]
    notes: Optional[str]
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class MedicalRecordWithDetailsEntity:
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