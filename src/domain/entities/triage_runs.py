from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.constants import TriageStatus, UrgencyLevel


@dataclass(frozen=True)
class TriageRunEntity:
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


@dataclass(frozen=True)
class TriageRunWithDetailsEntity:
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
    candidates: list
