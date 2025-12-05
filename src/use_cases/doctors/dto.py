from dataclasses import dataclass
from typing import Optional

from src.domain.constants import DoctorStatus
from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateDoctorDTO(BaseDTOMixin):
    bio: str
    experience_years: int
    license_number: str
    user_id: int
    specialization_id: int
    rating: float = 5.0
    status: DoctorStatus = DoctorStatus.PENDING


@dataclass
class AdminCreateDoctorDTO(BaseDTOMixin):
    bio: str
    experience_years: int
    license_number: str
    user_id: int
    specialization_id: int
    rating: float = 5.0
    status: DoctorStatus = DoctorStatus.APPROVED


@dataclass
class RegisterDoctorDTO(BaseDTOMixin):
    bio: str
    experience_years: int
    license_number: str
    specialization_id: int


@dataclass
class UpdateDoctorDTO(BaseDTOMixin):
    bio: Optional[str] = None
    rating: Optional[float] = None
    experience_years: Optional[int] = None
    specialization_id: Optional[int] = None
    license_number: Optional[str] = None


@dataclass
class ApproveDoctorDTO(BaseDTOMixin):
    status: DoctorStatus
    rejection_reason: Optional[str] = None
