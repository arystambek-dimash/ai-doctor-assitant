from datetime import datetime, date

from src.domain.constants import AppointmentStatus
from src.domain.entities.appointments import AppointmentEntity, AppointmentWithDetailsEntity
from src.domain.errors import BadRequestException, NotFoundException, ForbiddenException
from src.domain.interfaces.appointment_repository import IAppointmentRepository
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.schedule_repository import IScheduleRepository
from src.domain.interfaces.uow import IUoW
from src.use_cases.appointments.dto import CreateAppointmentDTO, UpdateAppointmentDTO


class AppointmentUseCase:
    def __init__(
            self,
            uow: IUoW,
            appointment_repository: IAppointmentRepository,
            doctor_repository: IDoctorRepository,
            schedule_repository: IScheduleRepository,
    ):
        self._uow = uow
        self._appointment_repo = appointment_repository
        self._doctor_repo = doctor_repository
        self._schedule_repo = schedule_repository

    async def create_appointment(
            self, appointment: CreateAppointmentDTO, user_id: int
    ) -> AppointmentEntity:
        if appointment.patient_id != user_id:
            raise ForbiddenException("Cannot book appointment for another user")

        if appointment.date_time <= datetime.now():
            raise BadRequestException("Cannot book appointment in the past")

        doctor = await self._doctor_repo.get_doctor_by_id(appointment.doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        await self._validate_appointment_slot(appointment.doctor_id, appointment.date_time)

        is_available = await self._appointment_repo.check_slot_availability(
            appointment.doctor_id, appointment.date_time
        )
        if not is_available:
            raise BadRequestException("This time slot is already booked")

        async with self._uow:
            created = await self._appointment_repo.create_appointment(appointment)
        return created

    async def update_appointment(
            self, appointment_id: int, appointment: UpdateAppointmentDTO, user_id: int, is_admin: bool = False
    ) -> AppointmentEntity:
        existing = await self._appointment_repo.get_appointment_by_id(appointment_id)
        if not existing:
            raise NotFoundException("Appointment not found")

        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        is_doctor = doctor and doctor.id == existing.doctor_id
        is_patient = user_id == existing.patient_id

        if not is_admin and not is_doctor and not is_patient:
            raise ForbiddenException("Access denied")

        if appointment.date_time:
            if appointment.date_time <= datetime.now():
                raise BadRequestException("Cannot reschedule to past time")

            await self._validate_appointment_slot(existing.doctor_id, appointment.date_time)

            is_available = await self._appointment_repo.check_slot_availability(
                existing.doctor_id, appointment.date_time
            )
            if not is_available:
                raise BadRequestException("This time slot is already booked")

        if appointment.status and not is_doctor and not is_admin:
            allowed_patient_statuses = [AppointmentStatus.CANCELLED]
            if appointment.status not in allowed_patient_statuses:
                raise ForbiddenException("Patients can only cancel appointments")

        async with self._uow:
            updated = await self._appointment_repo.update_appointment(appointment_id, appointment)
        return updated

    async def cancel_appointment(self, appointment_id: int, user_id: int) -> AppointmentEntity:
        existing = await self._appointment_repo.get_appointment_by_id(appointment_id)
        if not existing:
            raise NotFoundException("Appointment not found")

        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        is_doctor = doctor and doctor.id == existing.doctor_id
        is_patient = user_id == existing.patient_id

        if not is_doctor and not is_patient:
            raise ForbiddenException("Access denied")

        if existing.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            raise BadRequestException(f"Cannot cancel {existing.status.value} appointment")

        update_dto = UpdateAppointmentDTO(status=AppointmentStatus.CANCELLED)

        async with self._uow:
            updated = await self._appointment_repo.update_appointment(appointment_id, update_dto)
        return updated

    async def get_appointment_by_id(
            self, appointment_id: int, user_id: int, is_admin: bool = False
    ) -> AppointmentWithDetailsEntity:
        appointment = await self._appointment_repo.get_appointment_with_details(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment not found")

        if is_admin:
            return appointment

        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        is_doctor = doctor and doctor.id == appointment.doctor_id
        is_patient = user_id == appointment.patient_id

        if not is_doctor and not is_patient:
            raise ForbiddenException("Access denied")

        return appointment

    async def get_my_appointments(
            self,
            user_id: int,
            status: AppointmentStatus | None = None,
            skip: int = 0,
            limit: int = 20,
    ) -> list[AppointmentWithDetailsEntity]:
        return await self._appointment_repo.get_appointments_by_patient_id(
            user_id, status=status, skip=skip, limit=limit
        )

    async def get_doctor_appointments(
            self,
            doctor_id: int,
            user_id: int,
            is_admin: bool = False,
            status: AppointmentStatus | None = None,
            date_from: date | None = None,
            date_to: date | None = None,
            skip: int = 0,
            limit: int = 20,
    ) -> list[AppointmentWithDetailsEntity]:
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)

        if not is_admin and (not doctor or doctor.id != doctor_id):
            raise ForbiddenException("Access denied")

        return await self._appointment_repo.get_appointments_by_doctor_id(
            doctor_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )

    async def get_my_doctor_appointments(
            self,
            user_id: int,
            status: AppointmentStatus | None = None,
            date_from: date | None = None,
            date_to: date | None = None,
            skip: int = 0,
            limit: int = 20,
    ) -> list[AppointmentWithDetailsEntity]:
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            raise ForbiddenException("User is not a doctor")

        return await self._appointment_repo.get_appointments_by_doctor_id(
            doctor.id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )

    async def _validate_appointment_slot(self, doctor_id: int, date_time: datetime) -> None:
        day_of_week = date_time.weekday()
        appointment_time = date_time.time()

        schedule = await self._schedule_repo.get_schedule_by_doctor_and_day(doctor_id, day_of_week)

        if not schedule or not schedule.is_active:
            raise BadRequestException("Doctor is not available on this day")

        if appointment_time < schedule.start_time or appointment_time >= schedule.end_time:
            raise BadRequestException(
                f"Appointment time must be between {schedule.start_time} and {schedule.end_time}"
            )
