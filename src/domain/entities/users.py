from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserEntity:
    id: int
    email: str
    full_name: str
    password_hash: str
    phone: str
    is_admin: bool


@dataclass
class UserEntityWithDetails:
    id: int
    email: str
    full_name: str
    password_hash: str
    phone: str
    is_admin: bool
    is_doctor: bool
    doctor_id: int


@dataclass
class DoctorPatientEntity:
    """Patient entity as seen by a doctor - includes appointment stats."""
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    total_appointments: int
    last_appointment_date: Optional[datetime]
    upcoming_appointments: int
