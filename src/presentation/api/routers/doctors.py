from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, status

from src.domain.constants import DoctorStatus
from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.doctors import (
    DoctorRegisterRequest,
    DoctorUpdateRequest,
)
from src.presentation.api.schemas.responses.appointments import DoctorAvailabilityResponse
from src.presentation.api.schemas.responses.doctors import (
    DoctorResponse,
    DoctorWithDetailsResponse,
    DoctorPublicResponse,
    ApplicationStatusResponse,
    DoctorPatientResponse,
    DoctorPatientsStatsResponse,
)
from src.presentation.dependencies import (
    get_doctor_use_case,
    get_current_user,
    requires_roles,
    get_appointment_use_case,
)
from src.use_cases.appointments.use_case import AppointmentUseCase
from src.use_cases.doctors.dto import (
    RegisterDoctorDTO,
    UpdateDoctorDTO,
)
from src.use_cases.doctors.use_case import DoctorUseCase

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post(
    "/register",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_as_doctor(
        request: DoctorRegisterRequest,
        current_user: UserEntity = Depends(get_current_user),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await use_case.register_as_doctor(
        RegisterDoctorDTO(
            bio=request.bio,
            experience_years=request.experience_years,
            license_number=request.license_number,
            specialization_id=request.specialization_id,
        ),
        current_user.id
    )


@router.get(
    "/me",
    response_model=DoctorWithDetailsResponse
)
async def get_my_doctor_profile(
        current_user: UserEntity = Depends(get_current_user),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await use_case.get_my_doctor_profile(current_user.id)


@router.get(
    "/me/status",
    response_model=ApplicationStatusResponse
)
async def get_application_status(
        current_user: UserEntity = Depends(get_current_user),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await use_case.get_my_application_status(current_user.id)


@router.get(
    "/me/patients",
    response_model=List[DoctorPatientResponse],
)
async def get_my_patients(
        search: str = Query(None, description="Search by name, email or phone"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntity = Depends(requires_roles(is_doctor=True)),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    """Get all patients who have appointments with the current doctor."""
    return await use_case.get_my_patients(
        user_id=current_user.id,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/me/patients/stats",
    response_model=DoctorPatientsStatsResponse,
)
async def get_my_patients_stats(
        current_user: UserEntity = Depends(requires_roles(is_doctor=True)),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    """Get total patients and appointments count for the current doctor."""
    return await use_case.get_my_patients_stats(current_user.id)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT
)
async def withdraw_application(
        current_user: UserEntity = Depends(get_current_user),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await use_case.delete_doctor(current_user.id)


@router.get(
    "",
    response_model=List[DoctorWithDetailsResponse],
)
async def get_all_doctors(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        status: DoctorStatus = Query(None),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
        current_user: UserEntity = Depends(get_current_user),
):
    return await use_case.get_all_doctors(skip=skip, limit=limit,status=status, is_admin=current_user.is_admin)


@router.get(
    "/{doctor_id}",
    response_model=DoctorPublicResponse,
)
async def get_doctor(
        doctor_id: int,
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await use_case.get_doctor_by_id(doctor_id)


@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
async def update_doctor(
        doctor_id: int,
        request: DoctorUpdateRequest,
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
        current_user: UserEntity = Depends(requires_roles(is_doctor=True)),
):
    return await use_case.update_doctor(
        doctor_id,
        UpdateDoctorDTO(
            bio=request.bio,
            experience_years=request.experience_years,
            license_number=request.license_number,
            specialization_id=request.specialization_id,
        )
    )


@router.get(
    "/{doctor_id}/availability",
    response_model=DoctorAvailabilityResponse,
)
async def get_doctor_availability(
        doctor_id: int,
        target_date: date = Query(..., description="Date to check availability (YYYY-MM-DD)"),
        appointment_use_case: AppointmentUseCase = Depends(get_appointment_use_case),
):
    """Get available time slots for a doctor on a specific date."""
    return await appointment_use_case.get_doctor_availability(doctor_id, target_date)
