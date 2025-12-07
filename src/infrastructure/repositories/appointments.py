from datetime import datetime, date, timedelta
from typing import List

from sqlalchemy import insert, select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.constants import AppointmentStatus
from src.domain.entities.appointments import AppointmentEntity, AppointmentWithDetailsEntity
from src.domain.interfaces.appointment_repository import IAppointmentRepository
from src.infrastructure.database.models.appointments import Appointment
from src.infrastructure.database.models.doctors import Doctor
from src.use_cases.appointments.dto import CreateAppointmentDTO, UpdateAppointmentDTO


class AppointmentRepository(IAppointmentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_appointment(self, appointment: CreateAppointmentDTO) -> AppointmentEntity:
        stmt = (
            insert(Appointment)
            .values(**appointment.to_payload(exclude_none=True))
            .returning(Appointment)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_appointment(
            self, appointment_id: int, appointment: UpdateAppointmentDTO
    ) -> AppointmentEntity:
        stmt = (
            update(Appointment)
            .where(Appointment.id == appointment_id)
            .values(**appointment.to_payload(exclude_none=True))
            .returning(Appointment)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_appointment_by_id(self, appointment_id: int) -> AppointmentEntity | None:
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_appointment_with_details(
            self, appointment_id: int
    ) -> AppointmentWithDetailsEntity | None:
        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor).joinedload(Doctor.user),
                joinedload(Appointment.doctor).joinedload(Doctor.specialization),
            )
            .where(Appointment.id == appointment_id)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm_with_details(obj)

    async def get_appointments_by_patient_id(
            self,
            patient_id: int,
            status: AppointmentStatus | None = None,
            skip: int = 0,
            limit: int = 20,
    ) -> List[AppointmentWithDetailsEntity]:
        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor).joinedload(Doctor.user),
                joinedload(Appointment.doctor).joinedload(Doctor.specialization),
            )
            .where(Appointment.patient_id == patient_id)
        )

        if status:
            stmt = stmt.where(Appointment.status == status)

        stmt = stmt.order_by(Appointment.date_time.desc()).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        objects = result.scalars().unique().all()
        return [self._from_orm_with_details(obj) for obj in objects]

    async def get_appointments_by_doctor_id(
            self,
            doctor_id: int,
            status: AppointmentStatus | None = None,
            date_from: date | None = None,
            date_to: date | None = None,
            skip: int = 0,
            limit: int = 20,
    ) -> List[AppointmentWithDetailsEntity]:
        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor).joinedload(Doctor.user),
                joinedload(Appointment.doctor).joinedload(Doctor.specialization),
            )
            .where(Appointment.doctor_id == doctor_id)
        )

        if status:
            stmt = stmt.where(Appointment.status == status)

        if date_from:
            stmt = stmt.where(Appointment.date_time >= datetime.combine(date_from, datetime.min.time()))

        if date_to:
            stmt = stmt.where(Appointment.date_time <= datetime.combine(date_to, datetime.max.time()))

        stmt = stmt.order_by(Appointment.date_time.desc()).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        objects = result.scalars().unique().all()
        return [self._from_orm_with_details(obj) for obj in objects]

    async def get_doctor_appointments_for_date(
            self, doctor_id: int, target_date: date
    ) -> List[AppointmentEntity]:
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        stmt = (
            select(Appointment)
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.date_time >= start_of_day,
                    Appointment.date_time <= end_of_day,
                    Appointment.status.not_in([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]),
                )
            )
            .order_by(Appointment.date_time)
        )

        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def check_slot_availability(
            self, doctor_id: int, date_time: datetime, duration_minutes: int = 30
    ) -> bool:
        slot_end = date_time + timedelta(minutes=duration_minutes)

        stmt = (
            select(Appointment)
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.status.not_in([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]),
                    or_(
                        and_(
                            Appointment.date_time <= date_time,
                            Appointment.date_time + timedelta(minutes=duration_minutes) > date_time,
                        ),
                        and_(
                            Appointment.date_time < slot_end,
                            Appointment.date_time >= date_time,
                        ),
                    ),
                )
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is None

    async def delete_appointment(self, appointment_id: int) -> bool:
        stmt = delete(Appointment).where(Appointment.id == appointment_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    def _from_orm(obj: Appointment) -> AppointmentEntity:
        return AppointmentEntity(
            id=obj.id,
            date_time=obj.date_time,
            status=obj.status,
            notes=obj.notes,
            patient_id=obj.patient_id,
            doctor_id=obj.doctor_id,
            ai_consultation_id=obj.ai_consultation_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    def _from_orm_with_details(obj: Appointment) -> AppointmentWithDetailsEntity:
        return AppointmentWithDetailsEntity(
            id=obj.id,
            date_time=obj.date_time,
            status=obj.status,
            notes=obj.notes,
            patient_id=obj.patient_id,
            doctor_id=obj.doctor_id,
            ai_consultation_id=obj.ai_consultation_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            patient_name=obj.patient.full_name,
            patient_email=obj.patient.email,
            patient_phone=obj.patient.phone,
            doctor_name=obj.doctor.user.full_name,
            specialization_name=obj.doctor.specialization.name,
        )
