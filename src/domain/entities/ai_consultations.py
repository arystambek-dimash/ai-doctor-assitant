from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AIConsultationEntity:
    id: int
    symptoms_text: str
    recommended_specialization: str
    confidence: float
    ai_response_raw: str
    created_at: datetime
    patient_id: int


@dataclass(frozen=True)
class ChatMessageEntity:
    id: int
    consultation_id: int
    role: str  # "user", "assistant", "system"
    content: str
    created_at: datetime


@dataclass(frozen=True)
class AIRecommendation:
    specialization: str
    confidence: float
    reasoning: str
    urgency: str  # "low", "medium", "high", "emergency"
    suggested_doctors: list[int]
