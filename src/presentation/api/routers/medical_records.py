from fastapi import APIRouter, Depends, Query, status

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.medical_records import MedicalRecordCreateRequest, MedicalRecordUpdateRequest
from src.presentation.api.schemas.responses.medical_records import MedicalRecordResponse, \
    MedicalRecordWithDetailsResponse
from src.presentation.dependencies import get_current_user, get_medical_record_use_case
from src.use_cases.medical_records.dto import CreateMedicalRecordDTO, UpdateMedicalRecordDTO
from src.use_cases.medical_records.use_case import MedicalRecordUseCase

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


@router.post(
    "",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medical record (doctors only)",
)
async def create_medical_record(
        request: MedicalRecordCreateRequest,
        current_user: UserEntity = Depends(get_current_user),
        medical_record_use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    doctor = await medical_record_use_case._doctor_repo.get_doctor_by_user_id(current_user.id)

    dto = CreateMedicalRecordDTO(
        diagnosis=request.diagnosis,
        prescription=request.prescription,
        notes=request.notes,
        patient_id=request.patient_id,
        doctor_id=doctor.id,
        appointment_id=request.appointment_id,
    )
    return await medical_record_use_case.create_medical_record(dto, current_user.id)


@router.get(
    "/me",
    response_model=list[MedicalRecordWithDetailsResponse],
    summary="Get my medical records (as patient)",
)
async def get_my_medical_records(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntity = Depends(get_current_user),
        medical_record_use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    return await medical_record_use_case.get_my_medical_records(
        current_user.id, skip=skip, limit=limit
    )


@router.get(
    "/patient/{patient_id}",
    response_model=list[MedicalRecordWithDetailsResponse],
    summary="Get medical records by patient ID",
)
async def get_patient_medical_records(
        patient_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntity = Depends(get_current_user),
        medical_record_use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    return await medical_record_use_case.get_patient_medical_records(
        patient_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[MedicalRecordWithDetailsResponse],
    summary="Get medical records by doctor ID",
)
async def get_doctor_medical_records(
        doctor_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntity = Depends(get_current_user),
        medical_record_use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    return await medical_record_use_case.get_doctor_medical_records(
        doctor_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{record_id}",
    response_model=MedicalRecordWithDetailsResponse,
    summary="Get medical record by ID",
)
async def get_medical_record(
        record_id: int,
        current_user: UserEntity = Depends(get_current_user),
        medical_record_use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    return await medical_record_use_case.get_medical_record_by_id(
        record_id, user_id=current_user.id, is_admin=current_user.is_admin
    )


@router.patch(
    "/{record_id}",
    response_model=MedicalRecordResponse,
    summary="Update medical record (doctors only)",
)
async def update_medical_record(
        record_id: int,
        request: MedicalRecordUpdateRequest,
        current_user: UserEntity = Depends(get_current_user),
        medical_record_use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    dto = UpdateMedicalRecordDTO(
        diagnosis=request.diagnosis,
        prescription=request.prescription,
        notes=request.notes,
    )
    return await medical_record_use_case.update_medical_record(record_id, dto, current_user.id)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete medical record",
)
async def delete_medical_record(
        record_id: int,
        current_user: UserEntity = Depends(get_current_user),
        medical_record_use_case: MedicalRecordUseCase = Depends(get_medical_record_use_case),
):
    await medical_record_use_case.delete_medical_record(
        record_id, user_id=current_user.id, is_admin=current_user.is_admin
    )
