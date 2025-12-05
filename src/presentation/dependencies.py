import jwt
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.app.container import AppContainer
from src.domain.errors import BadRequestException, UnauthorizedException
from src.domain.interfaces.ai_consultation_repository import IAIConsultationRepository
from src.domain.interfaces.appointment_repository import IAppointmentRepository
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.medical_record_repositories import IMedicalRecordRepository
from src.domain.interfaces.schedule_repository import IScheduleRepository
from src.domain.interfaces.speicailization_repository import ISpecializationRepository
from src.domain.interfaces.uow import IUoW
from src.domain.interfaces.user_repository import IUserRepository
from src.infrastructure.services.jwt_service import JWTService
from src.infrastructure.services.openai_service import OpenAIService
from src.infrastructure.services.password_service import PasswordService
from src.use_cases.ai_consultations.use_case import AIConsultationUseCase
from src.use_cases.appointments.use_case import AppointmentUseCase
from src.use_cases.doctors.use_case import DoctorUseCase
from src.use_cases.handlers.ai_chat_handler import AIChatHandler, AIChatStartHandler
from src.use_cases.medical_records.use_case import MedicalRecordUseCase
from src.use_cases.schedules.use_case import ScheduleUseCase
from src.use_cases.specializations.use_case import SpecializationUseCase
from src.use_cases.users.use_case import UserUseCase

http_bearer = HTTPBearer()


@inject
async def get_user_use_case(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        user_repository: IUserRepository = Depends(Provide[AppContainer.user_repository]),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
        password_service: PasswordService = Depends(Provide[AppContainer.password_service])
) -> UserUseCase:
    return UserUseCase(
        uow=uow,
        user_repository=user_repository,
        jwt_service=jwt_service,
        password_service=password_service,
    )


@inject
async def get_doctor_use_case(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        doctor_repository: IDoctorRepository = Depends(Provide[AppContainer.doc_repository]),
        user_repository: IUserRepository = Depends(Provide[AppContainer.user_repository]),
        specialization_repository: ISpecializationRepository = Depends(Provide[AppContainer.specialization_repository]),
) -> DoctorUseCase:
    return DoctorUseCase(
        uow=uow,
        doctor_repository=doctor_repository,
        user_repository=user_repository,
        specialization_repository=specialization_repository,
    )


@inject
async def get_specialization_use_case(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        specialization_repository: ISpecializationRepository = Depends(Provide[AppContainer.specialization_repository]),
) -> SpecializationUseCase:
    return SpecializationUseCase(
        uow=uow,
        specialization_repository=specialization_repository,
    )


@inject
async def get_schedule_use_case(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        schedule_repository: IScheduleRepository = Depends(Provide[AppContainer.schedule_repository]),
        doctor_repository: IDoctorRepository = Depends(Provide[AppContainer.doc_repository]),
) -> ScheduleUseCase:
    return ScheduleUseCase(
        uow=uow,
        schedule_repository=schedule_repository,
        doctor_repository=doctor_repository,
    )


@inject
async def get_medical_record_use_case(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        medical_record_repository: IMedicalRecordRepository = Depends(Provide[AppContainer.medical_record_repository]),
        doctor_repository: IDoctorRepository = Depends(Provide[AppContainer.doc_repository]),
) -> MedicalRecordUseCase:
    return MedicalRecordUseCase(
        uow=uow,
        medical_record_repository=medical_record_repository,
        doctor_repository=doctor_repository,
    )


@inject
async def get_appointment_use_case(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        appointment_repository: IAppointmentRepository = Depends(Provide[AppContainer.appointment_repository]),
        doctor_repository: IDoctorRepository = Depends(Provide[AppContainer.doc_repository]),
        schedule_repository: IScheduleRepository = Depends(Provide[AppContainer.schedule_repository]),
) -> AppointmentUseCase:
    return AppointmentUseCase(
        uow=uow,
        appointment_repository=appointment_repository,
        doctor_repository=doctor_repository,
        schedule_repository=schedule_repository,
    )


@inject
async def get_ai_consultation_use_case(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        consultation_repository: IAIConsultationRepository = Depends(Provide[AppContainer.ai_consultation_repository]),
        doctor_repository: IDoctorRepository = Depends(Provide[AppContainer.doc_repository]),
        specialization_repository: ISpecializationRepository = Depends(Provide[AppContainer.specialization_repository]),
        openai_service: OpenAIService = Depends(Provide[AppContainer.openai_service]),
) -> AIConsultationUseCase:
    return AIConsultationUseCase(
        uow=uow,
        consultation_repository=consultation_repository,
        doctor_repository=doctor_repository,
        specialization_repository=specialization_repository,
        openai_service=openai_service,
    )


@inject
async def get_ai_chat_handler(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        consultation_repo: IAIConsultationRepository = Depends(Provide[AppContainer.ai_consultation_repository]),
        doctor_repo: IDoctorRepository = Depends(Provide[AppContainer.doc_repository]),
        specialization_repo: ISpecializationRepository = Depends(Provide[AppContainer.specialization_repository]),
        openai_service: OpenAIService = Depends(Provide[AppContainer.openai_service]),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
) -> AIChatHandler:
    return AIChatHandler(
        uow=uow,
        consultation_repo=consultation_repo,
        doctor_repo=doctor_repo,
        specialization_repo=specialization_repo,
        openai_service=openai_service,
        jwt_service=jwt_service,
    )


@inject
async def get_ai_chat_start_handler(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        consultation_repo: IAIConsultationRepository = Depends(Provide[AppContainer.ai_consultation_repository]),
        openai_service: OpenAIService = Depends(Provide[AppContainer.openai_service]),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
) -> AIChatStartHandler:
    return AIChatStartHandler(
        uow=uow,
        consultation_repo=consultation_repo,
        openai_service=openai_service,
        jwt_service=jwt_service,
    )


@inject
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
        user_repository: IUserRepository = Depends(Provide[AppContainer.user_repository]),
):
    try:
        token = credentials.credentials
        if not token:
            raise BadRequestException("Token is required")

        decoded_token = jwt_service.decode_access_token(token)

        user_id: int | None = decoded_token.get("sub")
        print(user_id)
        if not user_id:
            raise UnauthorizedException("Invalid token")
        return await user_repository.get_user_by_id(int(user_id))

    except jwt.ExpiredSignatureError:
        raise BadRequestException("Token is expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid token")
