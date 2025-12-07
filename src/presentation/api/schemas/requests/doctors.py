from typing import Optional

from pydantic import BaseModel, Field

from src.domain.constants import DoctorStatus


class DoctorRegisterRequest(BaseModel):
    bio: str = Field(..., min_length=10, max_length=2000)
    experience_years: int = Field(..., ge=0, le=70)
    license_number: str = Field(..., min_length=5, max_length=100)
    specialization_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "bio": "Experienced cardiologist with focus on preventive care.",
                "experience_years": 10,
                "license_number": "MD-12345-KZ",
                "specialization_id": 1
            }
        }


class AdminCreateDoctorRequest(BaseModel):
    user_id: int
    bio: str = Field(..., min_length=10, max_length=2000)
    experience_years: int = Field(..., ge=0, le=70)
    license_number: str = Field(..., min_length=5, max_length=100)
    specialization_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 5,
                "bio": "Experienced cardiologist with focus on preventive care.",
                "experience_years": 10,
                "license_number": "MD-12345-KZ",
                "specialization_id": 1
            }
        }


class DoctorUpdateRequest(BaseModel):
    bio: Optional[str] = Field(None, min_length=10, max_length=2000)
    experience_years: Optional[int] = Field(None, ge=0, le=70)
    license_number: Optional[str] = Field(None, min_length=5, max_length=100)
    specialization_id: Optional[int] = None


class AdminDoctorUpdateRequest(DoctorUpdateRequest):
    status: DoctorStatus = Field(...)
    rejection_reason: str = Field(..., min_length=10, max_length=500)
