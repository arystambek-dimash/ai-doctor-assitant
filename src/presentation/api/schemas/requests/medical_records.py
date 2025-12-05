from typing import Optional

from pydantic import BaseModel, Field


class MedicalRecordCreateRequest(BaseModel):
    diagnosis: str = Field(..., min_length=5, max_length=5000)
    prescription: Optional[str] = Field(None, max_length=5000)
    notes: Optional[str] = Field(None, max_length=5000)
    patient_id: int
    appointment_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis": "Acute bronchitis with mild respiratory symptoms",
                "prescription": "Amoxicillin 500mg - 3 times daily for 7 days",
                "notes": "Follow-up in 2 weeks if symptoms persist",
                "patient_id": 1,
                "appointment_id": 1
            }
        }


class MedicalRecordUpdateRequest(BaseModel):
    diagnosis: Optional[str] = Field(None, min_length=5, max_length=5000)
    prescription: Optional[str] = Field(None, max_length=5000)
    notes: Optional[str] = Field(None, max_length=5000)
