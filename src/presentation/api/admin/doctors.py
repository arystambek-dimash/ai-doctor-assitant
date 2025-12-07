from typing import List

from fastapi import APIRouter, status, Depends, Query

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.doctors import AdminCreateDoctorRequest, AdminDoctorUpdateRequest
from src.presentation.api.schemas.responses.doctors import DoctorResponse, DoctorWithDetailsResponse
from src.presentation.dependencies import get_current_user, get_doctor_use_case, requires_roles
from src.use_cases.doctors.dto import AdminCreateDoctorDTO, UpdateDoctorDTO
from src.use_cases.doctors.use_case import DoctorUseCase

router = APIRouter(prefix="/admin/doctors", tags=["Admin Doctors"])


@router.post(
    "/create",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED
)
async def admin_create_doctor(
        request: AdminCreateDoctorRequest,
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    return await use_case.admin_create_doctor(
        AdminCreateDoctorDTO(
            user_id=request.user_id,
            bio=request.bio,
            experience_years=request.experience_years,
            license_number=request.license_number,
            specialization_id=request.specialization_id,
        )
    )


@router.get(
    "/admin/pending",
    response_model=List[DoctorWithDetailsResponse]
)
async def get_pending_doctors(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    return await use_case.get_pending_doctors(
        skip=skip, limit=limit
    )


@router.patch(
    "/admin/{doctor_id}/update",
)
async def admin_update_doctor(
        doctor_id: int,
        request: AdminDoctorUpdateRequest,
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    return await use_case.update_doctor(
        doctor_id=doctor_id,
        dto=UpdateDoctorDTO(
            **request.dict(),
        )
    )


@router.delete(
    "/admin/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def admin_delete_doctor(
        doctor_id: int,
        use_case: DoctorUseCase = Depends(get_doctor_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    await use_case.delete_doctor(doctor_id)
