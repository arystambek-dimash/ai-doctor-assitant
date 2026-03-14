from typing import List, Optional

from src.domain.constants import TriageStatus, UrgencyLevel, DoctorStatus
from src.domain.entities.triage_candidates import TriageCandidateWithDoctorEntity
from src.domain.entities.triage_runs import (
    TriageRunEntity,
    TriageRunWithDetailsEntity,
)
from src.domain.errors import BadRequestException, NotFoundException, ForbiddenException
from src.domain.interfaces.chat_session_repository import IChatSessionRepository
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.specialization_repository import ISpecializationRepository
from src.domain.interfaces.triage_candidate_repository import ITriageCandidateRepository
from src.domain.interfaces.triage_run_repository import ITriageRunRepository
from src.domain.interfaces.uow import IUoW
from src.use_cases.triage.dto import (
    CreateTriageRunDTO,
    UpdateTriageRunDTO,
    CreateTriageCandidateDTO,
)


class TriageUseCase:
    def __init__(
        self,
        uow: IUoW,
        triage_run_repository: ITriageRunRepository,
        triage_candidate_repository: ITriageCandidateRepository,
        chat_session_repository: IChatSessionRepository,
        doctor_repository: IDoctorRepository,
        specialization_repository: ISpecializationRepository,
    ):
        self._uow = uow
        self._triage_run_repo = triage_run_repository
        self._candidate_repo = triage_candidate_repository
        self._session_repo = chat_session_repository
        self._doctor_repo = doctor_repository
        self._specialization_repo = specialization_repository

    async def create_triage_run(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
        trigger_message_id: Optional[int] = None,
        inputs_json: Optional[dict] = None,
        recommended_specialization_id: Optional[int] = None,
        urgency: Optional[UrgencyLevel] = None,
        confidence: Optional[float] = None,
        notes: Optional[str] = None,
        outputs_json: Optional[dict] = None,
        filters_json: Optional[dict] = None,
        model_name: Optional[str] = None,
        prompt_version: Optional[str] = None,
        temperature: Optional[float] = None,
        token_input: Optional[int] = None,
        token_output: Optional[int] = None,
        latency_ms: Optional[int] = None,
    ) -> TriageRunEntity:
        session = await self._session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        if recommended_specialization_id:
            spec = await self._specialization_repo.get_specialization_by_id(
                recommended_specialization_id
            )
            if not spec:
                raise NotFoundException("Specialization not found")

        dto = CreateTriageRunDTO(
            session_id=session_id,
            trigger_message_id=trigger_message_id,
            status=TriageStatus.SUCCESS,
            urgency=urgency,
            confidence=confidence,
            notes=notes,
            inputs_json=inputs_json,
            outputs_json=outputs_json,
            filters_json=filters_json,
            recommended_specialization_id=recommended_specialization_id,
            model_name=model_name,
            prompt_version=prompt_version,
            temperature=temperature,
            token_input=token_input,
            token_output=token_output,
            latency_ms=latency_ms,
        )

        async with self._uow:
            triage_run = await self._triage_run_repo.create_triage_run(dto)
        return triage_run

    async def update_triage_run(
        self,
        triage_run_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
        **kwargs,
    ) -> TriageRunEntity:
        triage_run = await self._triage_run_repo.get_triage_run_by_id(triage_run_id)
        if not triage_run:
            raise NotFoundException("Triage run not found")

        session = await self._session_repo.get_session_by_id(triage_run.session_id)
        if not is_admin and session and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        dto = UpdateTriageRunDTO(**{k: v for k, v in kwargs.items() if v is not None})

        async with self._uow:
            updated = await self._triage_run_repo.update_triage_run(triage_run_id, dto)
        return updated

    async def get_triage_run_by_id(
        self,
        triage_run_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> TriageRunWithDetailsEntity:
        triage_run = await self._triage_run_repo.get_triage_run_with_details(
            triage_run_id
        )
        if not triage_run:
            raise NotFoundException("Triage run not found")

        session = await self._session_repo.get_session_by_id(triage_run.session_id)
        if not is_admin and session and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        return triage_run

    async def get_triage_runs_by_session(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
        status: Optional[TriageStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[TriageRunEntity]:
        session = await self._session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        return await self._triage_run_repo.get_triage_runs_by_session_id(
            session_id, status=status, skip=skip, limit=limit
        )

    async def get_latest_triage_run(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> Optional[TriageRunWithDetailsEntity]:
        session = await self._session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        return await self._triage_run_repo.get_latest_triage_run_by_session_id(
            session_id
        )

    async def add_candidates(
        self,
        triage_run_id: int,
        candidates: List[dict],
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> List[TriageCandidateWithDoctorEntity]:
        triage_run = await self._triage_run_repo.get_triage_run_by_id(triage_run_id)
        if not triage_run:
            raise NotFoundException("Triage run not found")

        session = await self._session_repo.get_session_by_id(triage_run.session_id)
        if not is_admin and session and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        if not candidates:
            raise BadRequestException("Candidates list cannot be empty")

        candidate_dtos = []
        for idx, candidate in enumerate(candidates):
            doctor_id = candidate.get("doctor_id")
            if not doctor_id:
                raise BadRequestException(f"Missing doctor_id for candidate {idx + 1}")

            doctor = await self._doctor_repo.get_doctor_by_id(doctor_id)
            if not doctor:
                raise NotFoundException(f"Doctor {doctor_id} not found")

            if doctor.status != DoctorStatus.APPROVED:
                continue

            candidate_dtos.append(
                CreateTriageCandidateDTO(
                    triage_run_id=triage_run_id,
                    doctor_id=doctor_id,
                    rank=candidate.get("rank", idx + 1),
                    score=candidate.get("score", 0.0),
                    reason=candidate.get("reason"),
                    matched_filters_json=candidate.get("matched_filters_json"),
                )
            )

        async with self._uow:
            await self._candidate_repo.create_candidates_bulk(candidate_dtos)

        return await self._candidate_repo.get_candidates_by_triage_run_id(triage_run_id)

    async def get_candidates(
        self,
        triage_run_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> List[TriageCandidateWithDoctorEntity]:
        triage_run = await self._triage_run_repo.get_triage_run_by_id(triage_run_id)
        if not triage_run:
            raise NotFoundException("Triage run not found")

        session = await self._session_repo.get_session_by_id(triage_run.session_id)
        if not is_admin and session and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        return await self._candidate_repo.get_candidates_by_triage_run_id(triage_run_id)

    async def find_doctors_for_specialization(
        self,
        specialization_id: int,
        filters: Optional[dict] = None,
        limit: int = 10,
    ) -> List[dict]:
        """Find approved doctors for a given specialization with optional filters."""
        spec = await self._specialization_repo.get_specialization_by_id(
            specialization_id
        )
        if not spec:
            raise NotFoundException("Specialization not found")

        doctors = await self._doctor_repo.get_all_doctors(
            specialization_id=specialization_id,
            status=DoctorStatus.APPROVED,
            limit=limit,
        )

        results = []
        for doctor in doctors:
            score = self._calculate_doctor_score(doctor, filters)
            results.append({
                "doctor_id": doctor.id,
                "score": score,
                "reason": self._generate_reason(doctor, filters),
                "matched_filters_json": filters,
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        for idx, result in enumerate(results):
            result["rank"] = idx + 1

        return results

    @staticmethod
    def _calculate_doctor_score(doctor, filters: Optional[dict] = None) -> float:
        base_score = doctor.rating * 10
        experience_bonus = min(doctor.experience_years * 2, 20)
        return base_score + experience_bonus

    @staticmethod
    def _generate_reason(doctor, filters: Optional[dict] = None) -> str:
        reasons = []
        if doctor.rating >= 4.5:
            reasons.append("High rating")
        if doctor.experience_years >= 5:
            reasons.append("Experienced")
        return ", ".join(reasons) if reasons else "Matched criteria"
