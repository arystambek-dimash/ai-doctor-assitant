from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TriageCandidateEntity:
    id: int
    rank: int
    score: float
    reason: Optional[str]
    matched_filters_json: Optional[dict]
    triage_run_id: int
    doctor_id: int


@dataclass(frozen=True)
class TriageCandidateWithDoctorEntity:
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
