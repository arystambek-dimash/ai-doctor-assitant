from src.domain.entities.medical_records import MedicalRecordEntity, MedicalRecordWithDetailsEntity
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

    async def create_medical_record(
            self, record: CreateMedicalRecordDTO, user_id: int
    ) -> MedicalRecordEntity:
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            raise ForbiddenException("Only doctors can create medical records")

        if doctor.id != record.doctor_id:
            raise ForbiddenException("Cannot create medical record for another doctor")

        if record.appointment_id:
            existing = await self._medical_record_repo.get_medical_record_by_appointment_id(
                record.appointment_id
            )
            if existing:
                raise BadRequestException("Medical record already exists for this appointment")

        async with self._uow:
            created = await self._medical_record_repo.create_medical_record(record)
        return created

    async def update_medical_record(
            self, record_id: int, record: UpdateMedicalRecordDTO, user_id: int
    ) -> MedicalRecordEntity:
        existing = await self._medical_record_repo.get_medical_record_by_id(record_id)
        if not existing:
            raise NotFoundException("Medical record not found")

        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor or doctor.id != existing.doctor_id:
            raise ForbiddenException("Cannot update another doctor's medical record")

        async with self._uow:
            updated = await self._medical_record_repo.update_medical_record(record_id, record)
        return updated

    async def get_medical_record_by_id(
            self, record_id: int, user_id: int, is_admin: bool = False
    ) -> MedicalRecordWithDetailsEntity:
        record = await self._medical_record_repo.get_medical_record_with_details(record_id)
        if not record:
            raise NotFoundException("Medical record not found")

        if is_admin:
            return record

        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        is_doctor = doctor and doctor.id == record.doctor_id
        is_patient = user_id == record.patient_id

        if not is_doctor and not is_patient:
            raise ForbiddenException("Access denied to this medical record")

        return record

    async def get_my_medical_records(
            self, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[MedicalRecordWithDetailsEntity]:
        return await self._medical_record_repo.get_medical_records_by_patient_id(
            user_id, skip=skip, limit=limit
        )

    async def get_patient_medical_records(
            self, patient_id: int, user_id: int, is_admin: bool = False, skip: int = 0, limit: int = 20
    ) -> list[MedicalRecordWithDetailsEntity]:
        if is_admin or user_id == patient_id:
            return await self._medical_record_repo.get_medical_records_by_patient_id(
                patient_id, skip=skip, limit=limit
            )

        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            raise ForbiddenException("Access denied")

        records = await self._medical_record_repo.get_medical_records_by_patient_id(
            patient_id, skip=skip, limit=limit
        )
        return [r for r in records if r.doctor_id == doctor.id]

    async def get_doctor_medical_records(
            self, doctor_id: int, user_id: int, is_admin: bool = False, skip: int = 0, limit: int = 20
    ) -> list[MedicalRecordWithDetailsEntity]:
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)

        if not is_admin and (not doctor or doctor.id != doctor_id):
            raise ForbiddenException("Access denied to these medical records")

        return await self._medical_record_repo.get_medical_records_by_doctor_id(
            doctor_id, skip=skip, limit=limit
        )

    async def delete_medical_record(
            self, record_id: int, user_id: int, is_admin: bool = False
    ) -> bool:
        existing = await self._medical_record_repo.get_medical_record_by_id(record_id)
        if not existing:
            raise NotFoundException("Medical record not found")

        if not is_admin:
            doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
            if not doctor or doctor.id != existing.doctor_id:
                raise ForbiddenException("Cannot delete another doctor's medical record")

        async with self._uow:
            return await self._medical_record_repo.delete_medical_record(record_id)
