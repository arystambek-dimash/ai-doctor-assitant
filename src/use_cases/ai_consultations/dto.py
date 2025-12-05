from dataclasses import dataclass
from typing import Optional

from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateConsultationDTO(BaseDTOMixin):
    symptoms_text: str
    patient_id: int


@dataclass
class SendMessageDTO(BaseDTOMixin):
    consultation_id: int
    content: str


@dataclass
class UpdateConsultationDTO(BaseDTOMixin):
    recommended_specialization: Optional[str] = None
    confidence: Optional[float] = None
    ai_response_raw: Optional[str] = None
    status: Optional[str] = None