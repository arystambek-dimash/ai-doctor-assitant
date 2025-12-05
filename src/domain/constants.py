from enum import Enum
from enum import StrEnum


class UserRole(StrEnum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"


class DoctorStatus(str, Enum):
    PENDING = "pending"  # Awaiting admin approval
    APPROVED = "approved"  # Active doctor
    REJECTED = "rejected"  # Admin rejected
    SUSPENDED = "suspended"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
