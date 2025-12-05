from fastapi import APIRouter, Depends, Query, status

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.doctors import (
    DoctorRegisterRequest,
    AdminCreateDoctorRequest,
    DoctorUpdateRequest,
    RejectDoctorRequest,
)
from src.presentation.api.schemas.responses.doctors import (
    DoctorResponse,
    DoctorWithDetailsResponse,
    DoctorPublicResponse,
    ApplicationStatusResponse,
)
from src.presentation.dependencies import get_doctor_use_case, get_current_user
from src.use_cases.doctors.dto import (
    AdminCreateDoctorDTO,
    RegisterDoctorDTO,
    UpdateDoctorDTO,
)
from src.use_cases.doctors.use_case import DoctorUseCase

router = APIRouter(prefix="/doctors", tags=["Doctors"])


# ==================== USER SELF-REGISTRATION ====================

@router.post(
    "/register",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register as a doctor (requires admin approval)",
)
async def register_as_doctor(
        request: DoctorRegisterRequest,
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    dto = RegisterDoctorDTO(
        bio=request.bio,
        experience_years=request.experience_years,
        license_number=request.license_number,
        specialization_id=request.specialization_id,
    )
    return await doctor_use_case.register_as_doctor(dto, current_user.id)


@router.get(
    "/me",
    response_model=DoctorWithDetailsResponse,
    summary="Get my doctor profile",
)
async def get_my_doctor_profile(
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.get_my_doctor_profile(current_user.id)


@router.get(
    "/me/status",
    response_model=ApplicationStatusResponse,
    summary="Check my doctor application status",
)
async def get_application_status(
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.get_my_application_status(current_user.id)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Withdraw my pending doctor application",
)
async def withdraw_application(
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    doctor = await doctor_use_case._doctor_repo.get_doctor_by_user_id(current_user.id)
    if doctor:
        await doctor_use_case.delete_doctor(doctor.id, current_user.id)


# ==================== ADMIN OPERATIONS ====================

@router.post(
    "/admin/create",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Create doctor for existing user",
)
async def admin_create_doctor(
        request: AdminCreateDoctorRequest,
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    dto = AdminCreateDoctorDTO(
        user_id=request.user_id,
        bio=request.bio,
        experience_years=request.experience_years,
        license_number=request.license_number,
        specialization_id=request.specialization_id,
    )
    return await doctor_use_case.admin_create_doctor(dto, current_user.id, current_user.is_admin)


@router.get(
    "/admin/pending",
    response_model=list[DoctorWithDetailsResponse],
    summary="Admin: Get pending doctor applications",
)
async def get_pending_doctors(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.get_pending_doctors(
        current_user.id, current_user.is_admin, skip=skip, limit=limit
    )


@router.post(
    "/admin/{doctor_id}/approve",
    response_model=DoctorResponse,
    summary="Admin: Approve doctor application",
)
async def approve_doctor(
        doctor_id: int,
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.approve_doctor(doctor_id, current_user.id, current_user.is_admin)


@router.post(
    "/admin/{doctor_id}/reject",
    response_model=DoctorResponse,
    summary="Admin: Reject doctor application",
)
async def reject_doctor(
        doctor_id: int,
        request: RejectDoctorRequest,
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.reject_doctor(
        doctor_id, request.reason, current_user.id, current_user.is_admin
    )


@router.post(
    "/admin/{doctor_id}/suspend",
    response_model=DoctorResponse,
    summary="Admin: Suspend doctor",
)
async def suspend_doctor(
        doctor_id: int,
        request: RejectDoctorRequest,
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.suspend_doctor(
        doctor_id, request.reason, current_user.id, current_user.is_admin
    )


@router.post(
    "/admin/{doctor_id}/reinstate",
    response_model=DoctorResponse,
    summary="Admin: Reinstate suspended doctor",
)
async def reinstate_doctor(
        doctor_id: int,
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.reinstate_doctor(doctor_id, current_user.id, current_user.is_admin)


@router.delete(
    "/admin/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Admin: Delete doctor profile",
)
async def admin_delete_doctor(
        doctor_id: int,
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    await doctor_use_case.delete_doctor(doctor_id, current_user.id, current_user.is_admin)


# ==================== PUBLIC ENDPOINTS ====================

@router.get(
    "",
    response_model=list[DoctorPublicResponse],
    summary="Get all approved doctors",
)
async def get_all_doctors(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    doctors = await doctor_use_case.get_all_doctors(skip=skip, limit=limit, is_admin=False)
    return doctors


@router.get(
    "/specialization/{specialization_id}",
    response_model=list[DoctorPublicResponse],
    summary="Get approved doctors by specialization",
)
async def get_doctors_by_specialization(
        specialization_id: int,
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.get_doctors_by_specialization(specialization_id)


@router.get(
    "/{doctor_id}",
    response_model=DoctorPublicResponse,
    summary="Get doctor by ID (approved only)",
)
async def get_doctor(
        doctor_id: int,
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await doctor_use_case.get_doctor_by_id(doctor_id)


@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse,
    summary="Update doctor profile",
)
async def update_doctor(
        doctor_id: int,
        request: DoctorUpdateRequest,
        current_user: UserEntity = Depends(get_current_user),
        doctor_use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    dto = UpdateDoctorDTO(
        bio=request.bio,
        experience_years=request.experience_years,
        license_number=request.license_number,
        specialization_id=request.specialization_id,
    )
    return await doctor_use_case.update_doctor(
        doctor_id, dto, current_user.id, current_user.is_admin
    )
