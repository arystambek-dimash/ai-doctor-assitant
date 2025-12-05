from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.constants import DoctorStatus
from src.domain.entities.doctors import DoctorEntity, DoctorWithDetailsEntity
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.infrastructure.database.models.doctors import Doctor
from src.use_cases.doctors.dto import CreateDoctorDTO, UpdateDoctorDTO, ApproveDoctorDTO


class DoctorRepository(IDoctorRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_doctor(self, doctor: CreateDoctorDTO) -> DoctorEntity:
        stmt = (
            insert(Doctor)
            .values(**doctor.to_payload(exclude_none=True))
            .returning(Doctor)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_doctor(self, doctor_id: int, doctor: UpdateDoctorDTO) -> DoctorEntity:
        stmt = (
            update(Doctor)
            .where(Doctor.id == doctor_id)
            .values(**doctor.to_payload(exclude_none=True))
            .returning(Doctor)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_doctor_status(self, doctor_id: int, dto: ApproveDoctorDTO) -> DoctorEntity:
        stmt = (
            update(Doctor)
            .where(Doctor.id == doctor_id)
            .values(**dto.to_payload(exclude_none=True))
            .returning(Doctor)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_doctor_by_id(self, doctor_id: int) -> DoctorEntity | None:
        stmt = select(Doctor).where(Doctor.id == doctor_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_doctor_by_user_id(self, user_id: int) -> DoctorEntity | None:
        stmt = select(Doctor).where(Doctor.user_id == user_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_doctor_by_license_number(self, license_number: str) -> DoctorEntity | None:
        stmt = select(Doctor).where(Doctor.license_number == license_number)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_doctor_with_details(self, doctor_id: int) -> DoctorWithDetailsEntity | None:
        stmt = (
            select(Doctor)
            .options(joinedload(Doctor.user), joinedload(Doctor.specialization))
            .where(Doctor.id == doctor_id)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm_with_details(obj)

    async def get_all_doctors(
            self,
            status: DoctorStatus | None = None,
            skip: int = 0,
            limit: int = 10,
    ) -> list[DoctorWithDetailsEntity]:
        stmt = (
            select(Doctor)
            .options(joinedload(Doctor.user), joinedload(Doctor.specialization))
        )

        if status:
            stmt = stmt.where(Doctor.status == status)

        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        doctors = result.scalars().unique().all()
        return [self._from_orm_with_details(d) for d in doctors]

    async def get_doctors_by_specialization(
            self,
            specialization_id: int,
            only_approved: bool = True,
    ) -> list[DoctorWithDetailsEntity]:
        stmt = (
            select(Doctor)
            .options(joinedload(Doctor.user), joinedload(Doctor.specialization))
            .where(Doctor.specialization_id == specialization_id)
        )

        if only_approved:
            stmt = stmt.where(Doctor.status == DoctorStatus.APPROVED)

        result = await self._session.execute(stmt)
        doctors = result.scalars().unique().all()
        return [self._from_orm_with_details(d) for d in doctors]

    async def get_pending_doctors(self, skip: int = 0, limit: int = 20) -> list[DoctorWithDetailsEntity]:
        stmt = (
            select(Doctor)
            .options(joinedload(Doctor.user), joinedload(Doctor.specialization))
            .where(Doctor.status == DoctorStatus.PENDING)
            .order_by(Doctor.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        doctors = result.scalars().unique().all()
        return [self._from_orm_with_details(d) for d in doctors]

    async def delete_doctor(self, doctor_id: int) -> bool:
        stmt = delete(Doctor).where(Doctor.id == doctor_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    def _from_orm(obj: Doctor) -> DoctorEntity:
        return DoctorEntity(
            id=obj.id,
            bio=obj.bio,
            rating=obj.rating,
            experience_years=obj.experience_years,
            license_number=obj.license_number,
            status=obj.status,
            rejection_reason=obj.rejection_reason,
            user_id=obj.user_id,
            specialization_id=obj.specialization_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    def _from_orm_with_details(obj: Doctor) -> DoctorWithDetailsEntity:
        return DoctorWithDetailsEntity(
            id=obj.id,
            bio=obj.bio,
            rating=obj.rating,
            experience_years=obj.experience_years,
            license_number=obj.license_number,
            status=obj.status,
            rejection_reason=obj.rejection_reason,
            user_id=obj.user_id,
            specialization_id=obj.specialization_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            full_name=obj.user.full_name,
            email=obj.user.email,
            phone=obj.user.phone,
            specialization_name=obj.specialization.title,
        )
