from typing import Callable, Awaitable, Optional, AsyncGenerator

import jwt
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.container import AppContainer
from src.domain.entities.users import UserEntityWithDetails
from src.domain.errors import UnauthorizedException
from src.infrastructure.database.uow import UoW
from src.infrastructure.repositories.appointments import AppointmentRepository
from src.infrastructure.repositories.chat_messages import ChatMessageRepository
from src.infrastructure.repositories.chat_sessions import ChatSessionRepository
from src.infrastructure.repositories.doctors import DoctorRepository
from src.infrastructure.repositories.medical_records import MedicalRecordRepository
from src.infrastructure.repositories.schedules import ScheduleRepository
from src.infrastructure.repositories.specializations import SpecializationRepository
from src.infrastructure.repositories.triage_candidates import TriageCandidateRepository
from src.infrastructure.repositories.triage_runs import TriageRunRepository
from src.infrastructure.repositories.users import UserRepository
from src.infrastructure.services.jwt_service import JWTService
from src.infrastructure.services.openai_service import OpenAIService
from src.infrastructure.services.password_service import PasswordService
from src.use_cases.appointments.use_case import AppointmentUseCase
from src.use_cases.chat.use_case import ChatUseCase
from src.use_cases.doctors.use_case import DoctorUseCase
from src.use_cases.medical_records.use_case import MedicalRecordUseCase
from src.use_cases.schedules.use_case import ScheduleUseCase
from src.use_cases.specializations.use_case import SpecializationUseCase
from src.use_cases.stats.use_case import StatsUseCase
from src.use_cases.triage.use_case import TriageUseCase
from src.use_cases.users.use_case import UserUseCase

http_bearer = HTTPBearer()
http_bearer_optional = HTTPBearer(auto_error=False)


@inject
async def get_db_session(
        session_factory: async_sessionmaker = Depends(Provide[AppContainer.session_factory]),
) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session per request with proper cleanup."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@inject
async def get_user_use_case(
        session: AsyncSession = Depends(get_db_session),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
        password_service: PasswordService = Depends(Provide[AppContainer.password_service])
) -> UserUseCase:
    return UserUseCase(
        uow=UoW(session),
        user_repository=UserRepository(session),
        jwt_service=jwt_service,
        password_service=password_service,
    )


async def get_doctor_use_case(
        session: AsyncSession = Depends(get_db_session),
) -> DoctorUseCase:
    return DoctorUseCase(
        uow=UoW(session),
        doctor_repository=DoctorRepository(session),
        user_repository=UserRepository(session),
        specialization_repository=SpecializationRepository(session),
        appointment_repository=AppointmentRepository(session),
    )


async def get_specialization_use_case(
        session: AsyncSession = Depends(get_db_session),
) -> SpecializationUseCase:
    return SpecializationUseCase(
        uow=UoW(session),
        specialization_repository=SpecializationRepository(session),
    )


async def get_schedule_use_case(
        session: AsyncSession = Depends(get_db_session),
) -> ScheduleUseCase:
    return ScheduleUseCase(
        uow=UoW(session),
        schedule_repository=ScheduleRepository(session),
        doctor_repository=DoctorRepository(session),
        appointment_repository=AppointmentRepository(session),
    )


async def get_medical_record_use_case(
        session: AsyncSession = Depends(get_db_session),
) -> MedicalRecordUseCase:
    return MedicalRecordUseCase(
        uow=UoW(session),
        medical_record_repository=MedicalRecordRepository(session),
        doctor_repository=DoctorRepository(session),
    )


async def get_appointment_use_case(
        session: AsyncSession = Depends(get_db_session),
) -> AppointmentUseCase:
    return AppointmentUseCase(
        uow=UoW(session),
        appointment_repository=AppointmentRepository(session),
        doctor_repository=DoctorRepository(session),
        schedule_repository=ScheduleRepository(session),
    )


async def get_chat_use_case(
        session: AsyncSession = Depends(get_db_session),
) -> ChatUseCase:
    return ChatUseCase(
        uow=UoW(session),
        chat_session_repository=ChatSessionRepository(session),
        chat_message_repository=ChatMessageRepository(session),
    )


async def get_triage_use_case(
        session: AsyncSession = Depends(get_db_session),
) -> TriageUseCase:
    return TriageUseCase(
        uow=UoW(session),
        triage_run_repository=TriageRunRepository(session),
        triage_candidate_repository=TriageCandidateRepository(session),
        chat_session_repository=ChatSessionRepository(session),
        doctor_repository=DoctorRepository(session),
        specialization_repository=SpecializationRepository(session),
    )


async def get_stats_use_case(
        session: AsyncSession = Depends(get_db_session),
) -> StatsUseCase:
    return StatsUseCase(
        uow=UoW(session),
        user_repository=UserRepository(session),
        doctor_repository=DoctorRepository(session),
        appointment_repository=AppointmentRepository(session),
        medical_record_repository=MedicalRecordRepository(session),
    )


@inject
def get_openai_service(
        openai_service: OpenAIService = Depends(Provide[AppContainer.openai_service]),
) -> OpenAIService:
    return openai_service


@inject
async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
        session: AsyncSession = Depends(get_db_session),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
) -> UserEntityWithDetails:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException("Token is required")

    try:
        decoded = jwt_service.decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token is expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid token")

    sub = decoded.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise UnauthorizedException("Invalid token")

    user_repository = UserRepository(session)
    user = await user_repository.get_user_with_details(user_id)
    if user is None:
        raise UnauthorizedException("Invalid token")

    return user


@inject
async def get_current_user_optional(
        credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_optional),
        session: AsyncSession = Depends(get_db_session),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
) -> Optional[UserEntityWithDetails]:
    if credentials is None or not credentials.credentials:
        return None

    try:
        decoded = jwt_service.decode_access_token(credentials.credentials)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

    sub = decoded.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        return None

    user_repository = UserRepository(session)
    return await user_repository.get_user_with_details(user_id)


def requires_roles(*, is_admin: bool = False, is_doctor: bool = False) -> Callable[
    ..., Awaitable[UserEntityWithDetails]]:
    async def dependency(user: UserEntityWithDetails = Depends(get_current_user)) -> UserEntityWithDetails:
        if not is_admin and not is_doctor:
            return user

        allowed = (is_admin and user.is_admin) or (is_doctor and user.is_doctor)
        if not allowed:
            raise UnauthorizedException("You do not have permission to access this resource")

        return user

    return dependency
