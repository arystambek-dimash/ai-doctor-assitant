from typing import Optional

from pydantic import BaseModel, Field

from src.domain.constants import ChatSource, MessageRole, ContentType


class ChatSessionCreateRequest(BaseModel):
    source: ChatSource = ChatSource.WEB
    locale: Optional[str] = Field("ru", max_length=10)
    context_json: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "source": "web",
                "locale": "ru",
                "context_json": {"city": "Almaty"}
            }
        }


class ChatMessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    role: MessageRole = MessageRole.USER
    content_type: ContentType = ContentType.TEXT

    class Config:
        json_schema_extra = {
            "example": {
                "content": "I have a headache and feel tired",
                "role": "user",
                "content_type": "text"
            }
        }


class TriageRunCreateRequest(BaseModel):
    trigger_message_id: Optional[int] = None
    inputs_json: Optional[dict] = None
    recommended_specialization_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "trigger_message_id": 1,
                "inputs_json": {"symptoms": "headache, fatigue"},
                "recommended_specialization_id": 1
            }
        }


class TriageCandidateRequest(BaseModel):
    doctor_id: int
    rank: int = Field(..., ge=1)
    score: float = Field(..., ge=0, le=100)
    reason: Optional[str] = Field(None, max_length=500)
    matched_filters_json: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "doctor_id": 1,
                "rank": 1,
                "score": 85.5,
                "reason": "High rating, experienced"
            }
        }


class AddCandidatesRequest(BaseModel):
    candidates: list[TriageCandidateRequest]

    class Config:
        json_schema_extra = {
            "example": {
                "candidates": [
                    {"doctor_id": 1, "rank": 1, "score": 85.5, "reason": "Best match"},
                    {"doctor_id": 2, "rank": 2, "score": 78.0, "reason": "Good match"}
                ]
            }
        }
