from typing import List, Optional

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.constants import TriageStatus
from src.domain.entities.triage_candidates import TriageCandidateWithDoctorEntity
from src.domain.entities.triage_runs import (
    TriageRunEntity,
    TriageRunWithDetailsEntity,
)
from src.domain.interfaces.triage_run_repository import ITriageRunRepository
from src.infrastructure.database.models.doctors import Doctor
from src.infrastructure.database.models.triage_candidates import TriageCandidate
from src.infrastructure.database.models.triage_runs import TriageRun
from src.use_cases.triage.dto import CreateTriageRunDTO, UpdateTriageRunDTO


class TriageRunRepository(ITriageRunRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_triage_run(self, triage_run: CreateTriageRunDTO) -> TriageRunEntity:
        stmt = (
            insert(TriageRun)
            .values(**triage_run.to_payload(exclude_none=True))
            .returning(TriageRun)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_triage_run(
        self, triage_run_id: int, triage_run: UpdateTriageRunDTO
    ) -> TriageRunEntity:
        stmt = (
            update(TriageRun)
            .where(TriageRun.id == triage_run_id)
            .values(**triage_run.to_payload(exclude_none=True))
            .returning(TriageRun)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_triage_run_by_id(
        self, triage_run_id: int
    ) -> Optional[TriageRunEntity]:
        stmt = select(TriageRun).where(TriageRun.id == triage_run_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_triage_run_with_details(
        self, triage_run_id: int
    ) -> Optional[TriageRunWithDetailsEntity]:
        stmt = (
            select(TriageRun)
            .options(
                joinedload(TriageRun.recommended_specialization),
                joinedload(TriageRun.candidates)
                .joinedload(TriageCandidate.doctor)
                .joinedload(Doctor.user),
                joinedload(TriageRun.candidates)
                .joinedload(TriageCandidate.doctor)
                .joinedload(Doctor.specialization),
            )
            .where(TriageRun.id == triage_run_id)
        )
        result = await self._session.execute(stmt)
        obj = result.unique().scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm_with_details(obj)

    async def get_triage_runs_by_session_id(
        self,
        session_id: int,
        status: Optional[TriageStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[TriageRunEntity]:
        stmt = select(TriageRun).where(TriageRun.session_id == session_id)

        if status:
            stmt = stmt.where(TriageRun.status == status)

        stmt = stmt.order_by(TriageRun.created_at.desc()).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def get_latest_triage_run_by_session_id(
        self, session_id: int
    ) -> Optional[TriageRunWithDetailsEntity]:
        stmt = (
            select(TriageRun)
            .options(
                joinedload(TriageRun.recommended_specialization),
                joinedload(TriageRun.candidates)
                .joinedload(TriageCandidate.doctor)
                .joinedload(Doctor.user),
                joinedload(TriageRun.candidates)
                .joinedload(TriageCandidate.doctor)
                .joinedload(Doctor.specialization),
            )
            .where(TriageRun.session_id == session_id)
            .order_by(TriageRun.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        obj = result.unique().scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm_with_details(obj)

    @staticmethod
    def _from_orm(obj: TriageRun) -> TriageRunEntity:
        return TriageRunEntity(
            id=obj.id,
            status=obj.status,
            urgency=obj.urgency,
            confidence=obj.confidence,
            notes=obj.notes,
            inputs_json=obj.inputs_json,
            outputs_json=obj.outputs_json,
            filters_json=obj.filters_json,
            model_name=obj.model_name,
            prompt_version=obj.prompt_version,
            temperature=obj.temperature,
            token_input=obj.token_input,
            token_output=obj.token_output,
            latency_ms=obj.latency_ms,
            error_message=obj.error_message,
            session_id=obj.session_id,
            trigger_message_id=obj.trigger_message_id,
            recommended_specialization_id=obj.recommended_specialization_id,
            created_at=obj.created_at,
        )

    @staticmethod
    def _from_orm_candidate(obj: TriageCandidate) -> TriageCandidateWithDoctorEntity:
        return TriageCandidateWithDoctorEntity(
            id=obj.id,
            rank=obj.rank,
            score=obj.score,
            reason=obj.reason,
            matched_filters_json=obj.matched_filters_json,
            triage_run_id=obj.triage_run_id,
            doctor_id=obj.doctor_id,
            doctor_name=obj.doctor.user.full_name,
            doctor_bio=obj.doctor.bio,
            doctor_rating=obj.doctor.rating,
            doctor_experience_years=obj.doctor.experience_years,
            specialization_name=obj.doctor.specialization.title,
        )

    @staticmethod
    def _from_orm_with_details(obj: TriageRun) -> TriageRunWithDetailsEntity:
        candidates = [
            TriageRunRepository._from_orm_candidate(c)
            for c in sorted(obj.candidates, key=lambda x: x.rank)
        ]
        return TriageRunWithDetailsEntity(
            id=obj.id,
            status=obj.status,
            urgency=obj.urgency,
            confidence=obj.confidence,
            notes=obj.notes,
            inputs_json=obj.inputs_json,
            outputs_json=obj.outputs_json,
            filters_json=obj.filters_json,
            model_name=obj.model_name,
            prompt_version=obj.prompt_version,
            temperature=obj.temperature,
            token_input=obj.token_input,
            token_output=obj.token_output,
            latency_ms=obj.latency_ms,
            error_message=obj.error_message,
            session_id=obj.session_id,
            trigger_message_id=obj.trigger_message_id,
            recommended_specialization_id=obj.recommended_specialization_id,
            created_at=obj.created_at,
            specialization_name=(
                obj.recommended_specialization.title
                if obj.recommended_specialization
                else None
            ),
            candidates=candidates,
        )
