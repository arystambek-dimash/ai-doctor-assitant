from typing import List, Optional

from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.entities.triage_candidates import (
    TriageCandidateEntity,
    TriageCandidateWithDoctorEntity,
)
from src.domain.interfaces.triage_candidate_repository import ITriageCandidateRepository
from src.infrastructure.database.models.doctors import Doctor
from src.infrastructure.database.models.triage_candidates import TriageCandidate
from src.use_cases.triage.dto import CreateTriageCandidateDTO


class TriageCandidateRepository(ITriageCandidateRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_candidate(
        self, candidate: CreateTriageCandidateDTO
    ) -> TriageCandidateEntity:
        stmt = (
            insert(TriageCandidate)
            .values(**candidate.to_payload(exclude_none=True))
            .returning(TriageCandidate)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def create_candidates_bulk(
        self, candidates: List[CreateTriageCandidateDTO]
    ) -> List[TriageCandidateEntity]:
        if not candidates:
            return []

        values = [c.to_payload(exclude_none=True) for c in candidates]
        stmt = insert(TriageCandidate).values(values).returning(TriageCandidate)
        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def get_candidate_by_id(
        self, candidate_id: int
    ) -> Optional[TriageCandidateEntity]:
        stmt = select(TriageCandidate).where(TriageCandidate.id == candidate_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_candidates_by_triage_run_id(
        self, triage_run_id: int
    ) -> List[TriageCandidateWithDoctorEntity]:
        stmt = (
            select(TriageCandidate)
            .options(
                joinedload(TriageCandidate.doctor).joinedload(Doctor.user),
                joinedload(TriageCandidate.doctor).joinedload(Doctor.specialization),
            )
            .where(TriageCandidate.triage_run_id == triage_run_id)
            .order_by(TriageCandidate.rank)
        )
        result = await self._session.execute(stmt)
        objects = result.scalars().unique().all()
        return [self._from_orm_with_doctor(obj) for obj in objects]

    async def delete_candidates_by_triage_run_id(self, triage_run_id: int) -> int:
        stmt = delete(TriageCandidate).where(
            TriageCandidate.triage_run_id == triage_run_id
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    @staticmethod
    def _from_orm(obj: TriageCandidate) -> TriageCandidateEntity:
        return TriageCandidateEntity(
            id=obj.id,
            rank=obj.rank,
            score=obj.score,
            reason=obj.reason,
            matched_filters_json=obj.matched_filters_json,
            triage_run_id=obj.triage_run_id,
            doctor_id=obj.doctor_id,
        )

    @staticmethod
    def _from_orm_with_doctor(obj: TriageCandidate) -> TriageCandidateWithDoctorEntity:
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
