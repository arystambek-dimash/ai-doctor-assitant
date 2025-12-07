from typing import List

from fastapi import APIRouter, Depends, Query, status

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.doctors import (
    DoctorRegisterRequest,
    DoctorUpdateRequest,
)
from src.presentation.api.schemas.responses.doctors import (
    DoctorResponse,
    DoctorWithDetailsResponse,
    DoctorPublicResponse,
    ApplicationStatusResponse,
)
from src.presentation.dependencies import get_doctor_use_case, get_current_user, requires_roles
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
    response_model=List[DoctorPublicResponse],
)
async def get_all_doctors(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
):
    return await use_case.get_all_doctors(skip=skip, limit=limit, is_admin=False)


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
