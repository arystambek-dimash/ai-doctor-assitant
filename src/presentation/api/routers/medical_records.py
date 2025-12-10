from typing import List

from fastapi import APIRouter, Depends, Query, status

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.medical_records import MedicalRecordCreateRequest, MedicalRecordUpdateRequest
from src.presentation.api.schemas.responses.medical_records import MedicalRecordResponse, \
    MedicalRecordWithDetailsResponse
from src.presentation.dependencies import get_current_user, get_medical_record_use_case, requires_roles
from src.use_cases.medical_records.dto import CreateMedicalRecordDTO, UpdateMedicalRecordDTO
from src.use_cases.medical_records.use_case import MedicalRecordUseCase

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


@router.post(
    "",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_medical_record(
        request: MedicalRecordCreateRequest,
        use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
        current_user: UserEntity = Depends(requires_roles(is_doctor=True)),
):
    return await use_case.create_medical_record(
        CreateMedicalRecordDTO(
            diagnosis=request.diagnosis,
            prescription=request.prescription,
            notes=request.notes,
            patient_id=request.patient_id,
            appointment_id=request.appointment_id
        )
    )


@router.get(
    "/me",
    response_model=List[MedicalRecordWithDetailsResponse]
)
async def get_my_medical_records(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
        current_user: UserEntity = Depends(get_current_user),
):
    return await use_case.get_my_medical_records(
        current_user.id, skip=skip, limit=limit
    )


@router.get(
    "/patient/{patient_id}",
    response_model=List[MedicalRecordWithDetailsResponse]
)
async def get_patient_medical_records(
        patient_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntity = Depends(get_current_user),
        use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    return await use_case.get_patient_medical_records(
        patient_id,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[MedicalRecordWithDetailsResponse]
)
async def get_doctor_medical_records(
        doctor_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntity = Depends(get_current_user),
        use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    return await use_case.get_doctor_medical_records(
        doctor_id,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{record_id}",
    response_model=MedicalRecordWithDetailsResponse
)
async def get_medical_record(
        record_id: int,
        current_user: UserEntity = Depends(get_current_user),
        use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    return await use_case.get_medical_record_by_id(
        record_id, user_id=current_user.id, is_admin=current_user.is_admin
    )


@router.patch(
    "/{record_id}",
    response_model=MedicalRecordResponse
)
async def update_medical_record(
        record_id: int,
        request: MedicalRecordUpdateRequest,
        current_user: UserEntity = Depends(get_current_user),
        use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    dto = UpdateMedicalRecordDTO(
        diagnosis=request.diagnosis,
        prescription=request.prescription,
        notes=request.notes,
    )
    return await use_case.update_medical_record(record_id, dto, current_user.id)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_medical_record(
        record_id: int,
        current_user: UserEntity = Depends(get_current_user),
        use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    await use_case.delete_medical_record(
        record_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )
