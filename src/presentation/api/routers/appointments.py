from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, status

from src.domain.constants import AppointmentStatus
from src.domain.entities.users import UserEntityWithDetails
from src.presentation.api.schemas.requests.appointments import AppointmentCreateRequest, AppointmentUpdateRequest
from src.presentation.api.schemas.responses.appointments import AppointmentResponse, AppointmentWithDetailsResponse
from src.presentation.dependencies import get_current_user, get_appointment_use_case, requires_roles
from src.use_cases.appointments.dto import CreateAppointmentDTO, UpdateAppointmentDTO
from src.use_cases.appointments.use_case import AppointmentUseCase

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
        request: AppointmentCreateRequest,
        current_user: UserEntityWithDetails = Depends(get_current_user),
        use_case: AppointmentUseCase = Depends(get_appointment_use_case),
):
    return await use_case.create_appointment(
        CreateAppointmentDTO(
            date_time=request.date_time,
            doctor_id=request.doctor_id,
            patient_id=current_user.id,
            notes=request.notes,
            ai_consultation_id=request.ai_consultation_id,
        ),
        current_user.id
    )


@router.get(
    "/me",
    response_model=List[AppointmentWithDetailsResponse],
)
async def get_my_appointments(
        status: AppointmentStatus | None = Query(None),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntityWithDetails = Depends(get_current_user),
        use_case: AppointmentUseCase = Depends(get_appointment_use_case),
):
    return await use_case.get_my_appointments(
        current_user.id, status=status, skip=skip, limit=limit
    )


@router.get(
    "/doctor/me",
    response_model=List[AppointmentWithDetailsResponse],
)
async def get_my_doctor_appointments(
        status: AppointmentStatus | None = Query(None),
        date_from: date | None = Query(None),
        date_to: date | None = Query(None),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntityWithDetails = Depends(requires_roles(is_doctor=True)),
        use_case: AppointmentUseCase = Depends(get_appointment_use_case),
):
    return await use_case.get_my_doctor_appointments(
        current_user.id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/doctor/{doctor_id}",
    response_model=List[AppointmentWithDetailsResponse],
)
async def get_doctor_appointments(
        doctor_id: int,
        status: AppointmentStatus | None = Query(None),
        date_from: date | None = Query(None),
        date_to: date | None = Query(None),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntityWithDetails = Depends(get_current_user),
        use_case: AppointmentUseCase = Depends(get_appointment_use_case),
):
    return await use_case.get_doctor_appointments(
        doctor_id,
        current_user,
        status=status,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentWithDetailsResponse
)
async def get_appointment(
        appointment_id: int,
        current_user: UserEntityWithDetails = Depends(get_current_user),
        use_case: AppointmentUseCase = Depends(get_appointment_use_case),
):
    return await use_case.get_appointment_by_id(
        appointment_id, user_id=current_user.id, is_admin=current_user.is_admin
    )


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
async def update_appointment(
        appointment_id: int,
        request: AppointmentUpdateRequest,
        current_user: UserEntityWithDetails = Depends(get_current_user),
        use_case: AppointmentUseCase = Depends(get_appointment_use_case),
):
    return await use_case.update_appointment(
        appointment_id,
        UpdateAppointmentDTO(
            date_time=request.date_time,
            status=request.status,
            notes=request.notes,
        ),
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )


@router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse
)
async def cancel_appointment(
        appointment_id: int,
        current_user: UserEntityWithDetails = Depends(get_current_user),
        appointment_use_case: AppointmentUseCase = Depends(get_appointment_use_case),
):
    return await appointment_use_case.cancel_appointment(appointment_id, current_user.id)
