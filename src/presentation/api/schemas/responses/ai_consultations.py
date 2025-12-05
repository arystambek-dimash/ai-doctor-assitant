from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatMessageResponse(BaseModel):
    id: int
    consultation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConsultationResponse(BaseModel):
    id: int
    symptoms_text: str
    recommended_specialization: Optional[str]
    confidence: Optional[float]
    status: str
    created_at: datetime
    patient_id: int

    class Config:
        from_attributes = True


class ConsultationWithMessagesResponse(BaseModel):
    consultation: ConsultationResponse
    messages: list[ChatMessageResponse]


class ConsultationAnalysisResponse(BaseModel):
    analysis: dict
    recommended_doctors: list[dict]
