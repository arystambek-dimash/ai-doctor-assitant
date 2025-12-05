from src.infrastructure.utilities.model_mixins import IdMixin, TimeStampMixin
from .ai_consultations import AIConsultation
from .appointments import Appointment
from .doctors import Doctor
from .medical_records import MedicalRecord
from .schedules import Schedule
from .specializations import Specialization
from .users import User

__all__ = [
    "IdMixin",
    "TimeStampMixin",
    "User",
    "Doctor",
    "Specialization",
    "Schedule",
    "Appointment",
    "AIConsultation",
    "MedicalRecord",
]
