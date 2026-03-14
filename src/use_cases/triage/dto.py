from dataclasses import dataclass
from typing import Optional

from src.domain.constants import TriageStatus, UrgencyLevel
from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateTriageRunDTO(BaseDTOMixin):
    session_id: int
    trigger_message_id: Optional[int] = None
    status: TriageStatus = TriageStatus.SUCCESS
    urgency: Optional[UrgencyLevel] = None
    confidence: Optional[float] = None
    notes: Optional[str] = None
    inputs_json: Optional[dict] = None
    outputs_json: Optional[dict] = None
    filters_json: Optional[dict] = None
    recommended_specialization_id: Optional[int] = None
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    temperature: Optional[float] = None
    token_input: Optional[int] = None
    token_output: Optional[int] = None
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class UpdateTriageRunDTO(BaseDTOMixin):
    status: Optional[TriageStatus] = None
    urgency: Optional[UrgencyLevel] = None
    confidence: Optional[float] = None
    notes: Optional[str] = None
    outputs_json: Optional[dict] = None
    filters_json: Optional[dict] = None
    recommended_specialization_id: Optional[int] = None
    token_input: Optional[int] = None
    token_output: Optional[int] = None
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class CreateTriageCandidateDTO(BaseDTOMixin):
    triage_run_id: int
    doctor_id: int
    rank: int
    score: float
    reason: Optional[str] = None
    matched_filters_json: Optional[dict] = None
