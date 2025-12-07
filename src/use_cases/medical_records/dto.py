from dataclasses import dataclass
from typing import Optional

from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateMedicalRecordDTO(BaseDTOMixin):
    diagnosis: str
    patient_id: int
    prescription: Optional[str] = None
    notes: Optional[str] = None
    appointment_id: Optional[int] = None


@dataclass
class UpdateMedicalRecordDTO(BaseDTOMixin):
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    notes: Optional[str] = None
