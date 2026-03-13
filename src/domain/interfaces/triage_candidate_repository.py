from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.triage_candidates import (
    TriageCandidateEntity,
    TriageCandidateWithDoctorEntity,
)
from src.use_cases.triage.dto import CreateTriageCandidateDTO


class ITriageCandidateRepository(ABC):
    @abstractmethod
    async def create_candidate(
        self, candidate: CreateTriageCandidateDTO
    ) -> TriageCandidateEntity:
        pass

    @abstractmethod
    async def create_candidates_bulk(
        self, candidates: list[CreateTriageCandidateDTO]
    ) -> list[TriageCandidateEntity]:
        pass

    @abstractmethod
    async def get_candidate_by_id(
        self, candidate_id: int
    ) -> Optional[TriageCandidateEntity]:
        pass

    @abstractmethod
    async def get_candidates_by_triage_run_id(
        self, triage_run_id: int
    ) -> list[TriageCandidateWithDoctorEntity]:
        pass

    @abstractmethod
    async def delete_candidates_by_triage_run_id(self, triage_run_id: int) -> int:
        pass
