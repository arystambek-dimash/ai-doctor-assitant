from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.constants import (
    ChatSessionStatus,
    ChatSource,
    MessageRole,
    ContentType,
    TriageStatus,
    UrgencyLevel,
)


class ChatMessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    content_type: ContentType
    model_name: Optional[str]
    prompt_version: Optional[str]
    token_input: Optional[int]
    token_output: Optional[int]
    latency_ms: Optional[int]
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    status: ChatSessionStatus
    source: ChatSource
    locale: Optional[str]
    last_message_at: Optional[datetime]
    context_json: Optional[dict]
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSessionWithMessagesResponse(BaseModel):
    id: int
    status: ChatSessionStatus
    source: ChatSource
    locale: Optional[str]
    last_message_at: Optional[datetime]
    context_json: Optional[dict]
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse]

    class Config:
        from_attributes = True


class TriageCandidateResponse(BaseModel):
    id: int
    rank: int
    score: float
    reason: Optional[str]
    matched_filters_json: Optional[dict]
    triage_run_id: int
    doctor_id: int

    class Config:
        from_attributes = True


class TriageCandidateWithDoctorResponse(BaseModel):
    id: int
    rank: int
    score: float
    reason: Optional[str]
    matched_filters_json: Optional[dict]
    triage_run_id: int
    doctor_id: int
    doctor_name: str
    doctor_bio: str
    doctor_rating: float
    doctor_experience_years: int
    specialization_name: str

    class Config:
        from_attributes = True


class TriageRunResponse(BaseModel):
    id: int
    status: TriageStatus
    urgency: Optional[UrgencyLevel]
    confidence: Optional[float]
    notes: Optional[str]
    inputs_json: Optional[dict]
    outputs_json: Optional[dict]
    filters_json: Optional[dict]
    model_name: Optional[str]
    prompt_version: Optional[str]
    temperature: Optional[float]
    token_input: Optional[int]
    token_output: Optional[int]
    latency_ms: Optional[int]
    error_message: Optional[str]
    session_id: int
    trigger_message_id: Optional[int]
    recommended_specialization_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class TriageRunWithDetailsResponse(BaseModel):
    id: int
    status: TriageStatus
    urgency: Optional[UrgencyLevel]
    confidence: Optional[float]
    notes: Optional[str]
    inputs_json: Optional[dict]
    outputs_json: Optional[dict]
    filters_json: Optional[dict]
    model_name: Optional[str]
    prompt_version: Optional[str]
    temperature: Optional[float]
    token_input: Optional[int]
    token_output: Optional[int]
    latency_ms: Optional[int]
    error_message: Optional[str]
    session_id: int
    trigger_message_id: Optional[int]
    recommended_specialization_id: Optional[int]
    created_at: datetime
    specialization_name: Optional[str]
    candidates: list[TriageCandidateWithDoctorResponse]

    class Config:
        from_attributes = True
