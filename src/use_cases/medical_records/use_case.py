from typing import List

from src.domain.entities.medical_records import MedicalRecordEntity, MedicalRecordWithDetailsEntity
from src.domain.entities.users import UserEntity
from src.domain.errors import BadRequestException, NotFoundException, ForbiddenException
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.medical_record_repositories import IMedicalRecordRepository
from src.domain.interfaces.uow import IUoW
from src.use_cases.medical_records.dto import CreateMedicalRecordDTO, UpdateMedicalRecordDTO


class MedicalRecordUseCase:
    def __init__(
            self,
            uow: IUoW,
            medical_record_repository: IMedicalRecordRepository,
            doctor_repository: IDoctorRepository,
    ):
        self._uow = uow
        self._medical_record_repo = medical_record_repository
        self._doctor_repo = doctor_repository

    async def _get_record_or_404(self, record_id: int) -> MedicalRecordEntity:
        record = await self._medical_record_repo.get_medical_record_by_id(record_id)
        if not record:
            raise NotFoundException("Medical record not found")
        return record

    async def _get_doctor_by_user_or_none(self, user_id: int):
        return await self._doctor_repo.get_doctor_by_user_id(user_id)

    async def _assert_doctor_owns_record(self, user_id: int, record: MedicalRecordEntity) -> None:
        doctor = await self._get_doctor_by_user_or_none(user_id)
        if not doctor or doctor.id != record.doctor_id:
            raise ForbiddenException("Cannot modify another doctor's medical record")

    async def create_medical_record(
            self,
            record: CreateMedicalRecordDTO
    ) -> MedicalRecordEntity:
        if record.appointment_id is not None:
            existing = await self._medical_record_repo.get_medical_record_by_appointment_id(
                record.appointment_id
            )
            if existing:
                raise BadRequestException("Medical record already exists for this appointment")
        async with self._uow:
            return await self._medical_record_repo.create_medical_record(record)

    async def update_medical_record(
            self,
            record_id: int,
            record: UpdateMedicalRecordDTO,
            user_id: int
    ) -> MedicalRecordEntity:
        async with self._uow:
            existing = await self._get_record_or_404(record_id)
            await self._assert_doctor_owns_record(user_id, existing)
            return await self._medical_record_repo.update_medical_record(record_id, record)

    async def delete_medical_record(
            self, record_id: int,
            user_id: int,
            is_admin: bool = False
    ) -> bool:
        async with self._uow:
            existing = await self._get_record_or_404(record_id)
            if not is_admin:
                await self._assert_doctor_owns_record(user_id, existing)
            return await self._medical_record_repo.delete_medical_record(record_id)

    async def get_medical_record_by_id(
            self, record_id: int, user_id: int, is_admin: bool = False
    ) -> MedicalRecordWithDetailsEntity:
        record = await self._medical_record_repo.get_medical_record_with_details(record_id)
        if not record:
            raise NotFoundException("Medical record not found")

        if is_admin:
            return record

        doctor = await self._get_doctor_by_user_or_none(user_id)
        is_doctor_owner = bool(doctor) and doctor.id == record.doctor_id
        is_patient_owner = user_id == record.patient_id

        if not (is_doctor_owner or is_patient_owner):
            raise ForbiddenException("Access denied to this medical record")

        return record

    async def get_my_medical_records(
            self,
            user_id: int,
            skip: int = 0,
            limit: int = 20
    ) -> List[MedicalRecordWithDetailsEntity]:
        return await self._medical_record_repo.get_medical_records_by_patient_id(
            user_id, skip=skip, limit=limit
        )

    async def get_patient_medical_records(
            self,
            patient_id: int,
            current_user: UserEntity,
            skip: int = 0,
            limit: int = 20,
    ) -> List[MedicalRecordWithDetailsEntity]:
        if current_user.is_admin or current_user.id == patient_id:
            return await self._medical_record_repo.get_medical_records_by_patient_id(
                patient_id, skip=skip, limit=limit
            )
        doctor = await self._get_doctor_by_user_or_none(current_user.id)
        if not doctor:
            raise ForbiddenException("Access denied to these medical records")

        records = await self._medical_record_repo.get_medical_records_by_patient_id(
            patient_id, skip=skip, limit=limit
        )
        return [r for r in records if r.doctor_id == doctor.id]

    async def get_doctor_medical_records(
            self,
            doctor_id: int,
            current_user: UserEntity,
            skip: int = 0,
            limit: int = 20,
    ) -> list[MedicalRecordWithDetailsEntity]:
        if not current_user.is_admin:
            doctor = await self._get_doctor_by_user_or_none(current_user.id)
            if not doctor or doctor.id != doctor_id:
                raise ForbiddenException("Access denied to these medical records")

        return await self._medical_record_repo.get_medical_records_by_doctor_id(
            doctor_id, skip=skip, limit=limit
        )
