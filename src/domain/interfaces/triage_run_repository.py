from abc import ABC, abstractmethod
from typing import Optional

from src.domain.constants import TriageStatus
from src.domain.entities.triage_runs import (
    TriageRunEntity,
    TriageRunWithDetailsEntity,
)
from src.use_cases.triage.dto import CreateTriageRunDTO, UpdateTriageRunDTO


class ITriageRunRepository(ABC):
    @abstractmethod
    async def create_triage_run(self, triage_run: CreateTriageRunDTO) -> TriageRunEntity:
        pass

    @abstractmethod
    async def update_triage_run(
        self, triage_run_id: int, triage_run: UpdateTriageRunDTO
    ) -> TriageRunEntity:
        pass

    @abstractmethod
    async def get_triage_run_by_id(
        self, triage_run_id: int
    ) -> Optional[TriageRunEntity]:
        pass

    @abstractmethod
    async def get_triage_run_with_details(
        self, triage_run_id: int
    ) -> Optional[TriageRunWithDetailsEntity]:
        pass

    @abstractmethod
    async def get_triage_runs_by_session_id(
        self,
        session_id: int,
        status: Optional[TriageStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[TriageRunEntity]:
        pass

    @abstractmethod
    async def get_latest_triage_run_by_session_id(
        self, session_id: int
    ) -> Optional[TriageRunWithDetailsEntity]:
        pass
