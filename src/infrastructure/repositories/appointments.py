from datetime import datetime, date, timedelta
from typing import List, Optional

from sqlalchemy import insert, select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.constants import AppointmentStatus
from src.domain.entities.appointments import (
    AppointmentEntity,
    AppointmentWithDetailsEntity,
)
from src.domain.entities.users import DoctorPatientEntity
from src.infrastructure.database.models.users import User
from src.domain.interfaces.appointment_repository import IAppointmentRepository
from src.infrastructure.database.models.appointments import Appointment
from src.infrastructure.database.models.doctors import Doctor
from src.use_cases.appointments.dto import CreateAppointmentDTO, UpdateAppointmentDTO


class AppointmentRepository(IAppointmentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_appointment(
        self, appointment: CreateAppointmentDTO
    ) -> AppointmentEntity:
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

    async def get_appointment_by_id(
        self, appointment_id: int
    ) -> Optional[AppointmentEntity]:
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_appointment_with_details(
        self, appointment_id: int
    ) -> Optional[AppointmentWithDetailsEntity]:
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
        status: Optional[AppointmentStatus] = None,
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
        status: Optional[AppointmentStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
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
            stmt = stmt.where(
                Appointment.date_time >= datetime.combine(date_from, datetime.min.time())
            )

        if date_to:
            stmt = stmt.where(
                Appointment.date_time <= datetime.combine(date_to, datetime.max.time())
            )

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
                    Appointment.status.in_([
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED,
                        AppointmentStatus.IN_PROGRESS,
                    ]),
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
            select(func.count())
            .select_from(Appointment)
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.status.in_([
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED,
                    ]),
                    or_(
                        and_(
                            Appointment.date_time <= date_time,
                            Appointment.date_time
                            + func.make_interval(0, 0, 0, 0, 0, Appointment.duration_minutes)
                            > date_time,
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
        count = result.scalar_one()
        return count == 0

    async def delete_appointment(self, appointment_id: int) -> bool:
        stmt = delete(Appointment).where(Appointment.id == appointment_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def count_all_appointments(self) -> int:
        stmt = select(func.count()).select_from(Appointment)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_today_appointments(self) -> int:
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        stmt = (
            select(func.count())
            .select_from(Appointment)
            .where(
                and_(
                    Appointment.date_time >= start_of_day,
                    Appointment.date_time <= end_of_day,
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_appointments_by_status(self, status: AppointmentStatus) -> int:
        stmt = (
            select(func.count())
            .select_from(Appointment)
            .where(Appointment.status == status)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_doctor_patients(
        self,
        doctor_id: int,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[DoctorPatientEntity]:
        """Get all patients who have appointments with this doctor."""
        now = datetime.now()

        # Subquery for total appointments per patient with this doctor
        total_appts_subq = (
            select(
                Appointment.patient_id,
                func.count(Appointment.id).label("total_appointments"),
                func.max(Appointment.date_time).label("last_appointment_date"),
            )
            .where(Appointment.doctor_id == doctor_id)
            .group_by(Appointment.patient_id)
            .subquery()
        )

        # Subquery for upcoming appointments count
        upcoming_appts_subq = (
            select(
                Appointment.patient_id,
                func.count(Appointment.id).label("upcoming_appointments"),
            )
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.date_time >= now,
                    Appointment.status.in_([
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED,
                    ]),
                )
            )
            .group_by(Appointment.patient_id)
            .subquery()
        )

        # Main query
        stmt = (
            select(
                User,
                total_appts_subq.c.total_appointments,
                total_appts_subq.c.last_appointment_date,
                func.coalesce(upcoming_appts_subq.c.upcoming_appointments, 0).label("upcoming_appointments"),
            )
            .join(total_appts_subq, User.id == total_appts_subq.c.patient_id)
            .outerjoin(upcoming_appts_subq, User.id == upcoming_appts_subq.c.patient_id)
        )

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.phone.ilike(search_pattern),
                )
            )

        stmt = stmt.order_by(total_appts_subq.c.last_appointment_date.desc()).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            DoctorPatientEntity(
                id=row.User.id,
                email=row.User.email,
                full_name=row.User.full_name,
                phone=row.User.phone,
                total_appointments=row.total_appointments,
                last_appointment_date=row.last_appointment_date,
                upcoming_appointments=row.upcoming_appointments,
            )
            for row in rows
        ]

    async def count_doctor_patients(self, doctor_id: int) -> int:
        """Count distinct patients for a doctor."""
        stmt = (
            select(func.count(func.distinct(Appointment.patient_id)))
            .where(Appointment.doctor_id == doctor_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_doctor_appointments(
        self,
        doctor_id: int,
        status: Optional[AppointmentStatus] = None,
    ) -> int:
        """Count appointments for a doctor."""
        stmt = (
            select(func.count())
            .select_from(Appointment)
            .where(Appointment.doctor_id == doctor_id)
        )
        if status:
            stmt = stmt.where(Appointment.status == status)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    def _from_orm(obj: Appointment) -> AppointmentEntity:
        return AppointmentEntity(
            id=obj.id,
            date_time=obj.date_time,
            status=obj.status,
            duration_minutes=obj.duration_minutes,
            visit_type=obj.visit_type,
            notes=obj.notes,
            cancel_reason=obj.cancel_reason,
            patient_id=obj.patient_id,
            doctor_id=obj.doctor_id,
            triage_run_id=obj.triage_run_id,
            rescheduled_from_id=obj.rescheduled_from_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    def _from_orm_with_details(obj: Appointment) -> AppointmentWithDetailsEntity:
        return AppointmentWithDetailsEntity(
            id=obj.id,
            date_time=obj.date_time,
            status=obj.status,
            duration_minutes=obj.duration_minutes,
            visit_type=obj.visit_type,
            notes=obj.notes,
            cancel_reason=obj.cancel_reason,
            patient_id=obj.patient_id,
            doctor_id=obj.doctor_id,
            triage_run_id=obj.triage_run_id,
            rescheduled_from_id=obj.rescheduled_from_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            patient_name=obj.patient.full_name,
            patient_phone=obj.patient.phone,
            doctor_name=obj.doctor.user.full_name,
            specialization_name=obj.doctor.specialization.title,
        )
