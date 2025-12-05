from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.entities.medical_records import MedicalRecordEntity, MedicalRecordWithDetailsEntity
from src.domain.interfaces.medical_record_repositories import IMedicalRecordRepository
from src.infrastructure.database.models.doctors import Doctor
from src.infrastructure.database.models.medical_records import MedicalRecord
from src.use_cases.medical_records.dto import CreateMedicalRecordDTO, UpdateMedicalRecordDTO


class MedicalRecordRepository(IMedicalRecordRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_medical_record(self, record: CreateMedicalRecordDTO) -> MedicalRecordEntity:
        stmt = (
            insert(MedicalRecord)
            .values(**record.to_payload(exclude_none=True))
            .returning(MedicalRecord)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_medical_record(
            self, record_id: int, record: UpdateMedicalRecordDTO
    ) -> MedicalRecordEntity:
        stmt = (
            update(MedicalRecord)
            .where(MedicalRecord.id == record_id)
            .values(**record.to_payload(exclude_none=True))
            .returning(MedicalRecord)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_medical_record_by_id(self, record_id: int) -> MedicalRecordEntity | None:
        stmt = select(MedicalRecord).where(MedicalRecord.id == record_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_medical_record_with_details(
            self, record_id: int
    ) -> MedicalRecordWithDetailsEntity | None:
        stmt = (
            select(MedicalRecord)
            .options(
                joinedload(MedicalRecord.patient),
                joinedload(MedicalRecord.doctor).joinedload(Doctor.user),
                joinedload(MedicalRecord.doctor).joinedload(Doctor.specialization),
            )
            .where(MedicalRecord.id == record_id)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm_with_details(obj)

    async def get_medical_records_by_patient_id(
            self, patient_id: int, skip: int = 0, limit: int = 20
    ) -> list[MedicalRecordWithDetailsEntity]:
        stmt = (
            select(MedicalRecord)
            .options(
                joinedload(MedicalRecord.patient),
                joinedload(MedicalRecord.doctor).joinedload(Doctor.user),
                joinedload(MedicalRecord.doctor).joinedload(Doctor.specialization),
            )
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(MedicalRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        objects = result.scalars().unique().all()
        return [self._from_orm_with_details(obj) for obj in objects]

    async def get_medical_records_by_doctor_id(
            self, doctor_id: int, skip: int = 0, limit: int = 20
    ) -> list[MedicalRecordWithDetailsEntity]:
        stmt = (
            select(MedicalRecord)
            .options(
                joinedload(MedicalRecord.patient),
                joinedload(MedicalRecord.doctor).joinedload(Doctor.user),
                joinedload(MedicalRecord.doctor).joinedload(Doctor.specialization),
            )
            .where(MedicalRecord.doctor_id == doctor_id)
            .order_by(MedicalRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        objects = result.scalars().unique().all()
        return [self._from_orm_with_details(obj) for obj in objects]

    async def get_medical_record_by_appointment_id(
            self, appointment_id: int
    ) -> MedicalRecordEntity | None:
        stmt = select(MedicalRecord).where(MedicalRecord.appointment_id == appointment_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def delete_medical_record(self, record_id: int) -> bool:
        stmt = delete(MedicalRecord).where(MedicalRecord.id == record_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    def _from_orm(obj: MedicalRecord) -> MedicalRecordEntity:
        return MedicalRecordEntity(
            id=obj.id,
            diagnosis=obj.diagnosis,
            prescription=obj.prescription,
            notes=obj.notes,
            patient_id=obj.patient_id,
            doctor_id=obj.doctor_id,
            appointment_id=obj.appointment_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    def _from_orm_with_details(obj: MedicalRecord) -> MedicalRecordWithDetailsEntity:
        return MedicalRecordWithDetailsEntity(
            id=obj.id,
            diagnosis=obj.diagnosis,
            prescription=obj.prescription,
            notes=obj.notes,
            patient_id=obj.patient_id,
            doctor_id=obj.doctor_id,
            appointment_id=obj.appointment_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            patient_name=obj.patient.full_name,
            patient_email=obj.patient.email,
            doctor_name=obj.doctor.user.full_name,
            specialization_name=obj.doctor.specialization.name,
        )
