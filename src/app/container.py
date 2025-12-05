from typing import AsyncGenerator

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.app.settings import Settings
from src.infrastructure.database.core import create_engine, create_session_factory
from src.infrastructure.database.uow import UoW
from src.infrastructure.repositories.ai_consultations import AIConsultationRepository
from src.infrastructure.repositories.appointments import AppointmentRepository
from src.infrastructure.repositories.doctors import DoctorRepository
from src.infrastructure.repositories.medical_records import MedicalRecordRepository
from src.infrastructure.repositories.schedules import ScheduleRepository
from src.infrastructure.repositories.specializations import SpecializationRepository
from src.infrastructure.repositories.users import UserRepository
from src.infrastructure.services.jwt_service import JWTService
from src.infrastructure.services.openai_service import OpenAIService
from src.infrastructure.services.password_service import PasswordService


async def get_session(
        session_factory: async_sessionmaker[AsyncSession]
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.presentation.dependencies"
        ]
    )

    settings = providers.Singleton(Settings)

    engine = providers.Singleton(
        create_engine,
        db_url=settings.provided.db_url,
        echo=False
    )

    session_factory = providers.Singleton(
        create_session_factory,
        engine=engine
    )

    session = providers.Resource(get_session, session_factory=session_factory)
    jwt_service = providers.Singleton(
        JWTService,
        jwt_access_secret_key=settings.provided.JWT_ACCESS_TOKEN_SECRET_KEY,
        jwt_refresh_secret_key=settings.provided.JWT_REFRESH_TOKEN_SECRET_KEY,
    )
    password_service = providers.Singleton(
        PasswordService,
    )
    uow = providers.Factory(UoW, session=session)
    user_repository = providers.Factory(UserRepository, session=session)
    doc_repository = providers.Factory(DoctorRepository, session=session)
    specialization_repository = providers.Factory(SpecializationRepository, session=session)
    schedule_repository = providers.Factory(ScheduleRepository, session=session)
    medical_record_repository = providers.Factory(MedicalRecordRepository, session=session)
    appointment_repository = providers.Factory(AppointmentRepository, session=session)
    ai_consultation_repository = providers.Factory(AIConsultationRepository, session=session)
    openai_service = providers.Factory(OpenAIService, session=session)
