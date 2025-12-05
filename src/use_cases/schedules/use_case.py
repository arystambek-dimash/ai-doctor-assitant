from datetime import datetime, timedelta

from src.domain.entities.schedules import ScheduleEntity, TimeSlotEntity
from src.domain.errors import BadRequestException, NotFoundException, ForbiddenException
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.schedule_repository import IScheduleRepository
from src.domain.interfaces.uow import IUoW
from src.use_cases.schedules.dto import CreateScheduleDTO, UpdateScheduleDTO


class ScheduleUseCase:
    DAYS_OF_WEEK = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    def __init__(
            self,
            uow: IUoW,
            schedule_repository: IScheduleRepository,
            doctor_repository: IDoctorRepository,
    ):
        self._uow = uow
        self._schedule_repo = schedule_repository
        self._doctor_repo = doctor_repository

    async def create_schedule(self, schedule: CreateScheduleDTO, user_id: int) -> ScheduleEntity:
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            raise ForbiddenException("User is not a doctor")

        if doctor.id != schedule.doctor_id:
            raise ForbiddenException("Cannot create schedule for another doctor")

        self._validate_schedule(schedule)

        existing = await self._schedule_repo.get_schedule_by_doctor_and_day(
            schedule.doctor_id, schedule.day_of_week
        )
        if existing:
            day_name = self.DAYS_OF_WEEK.get(schedule.day_of_week, "Unknown")
            raise BadRequestException(f"Schedule already exists for {day_name}")

        async with self._uow:
            created = await self._schedule_repo.create_schedule(schedule)
        return created

    async def update_schedule(
            self, schedule_id: int, schedule: UpdateScheduleDTO, user_id: int
    ) -> ScheduleEntity:
        existing = await self._schedule_repo.get_schedule_by_id(schedule_id)
        if not existing:
            raise NotFoundException("Schedule not found")

        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor or doctor.id != existing.doctor_id:
            raise ForbiddenException("Cannot update another doctor's schedule")

        if schedule.day_of_week is not None and schedule.day_of_week != existing.day_of_week:
            day_exists = await self._schedule_repo.get_schedule_by_doctor_and_day(
                existing.doctor_id, schedule.day_of_week
            )
            if day_exists:
                day_name = self.DAYS_OF_WEEK.get(schedule.day_of_week, "Unknown")
                raise BadRequestException(f"Schedule already exists for {day_name}")

        self._validate_schedule_update(existing, schedule)

        async with self._uow:
            updated = await self._schedule_repo.update_schedule(schedule_id, schedule)
        return updated

    async def get_schedule_by_id(self, schedule_id: int) -> ScheduleEntity:
        schedule = await self._schedule_repo.get_schedule_by_id(schedule_id)
        if not schedule:
            raise NotFoundException("Schedule not found")
        return schedule

    async def get_schedules_by_doctor_id(self, doctor_id: int) -> list[ScheduleEntity]:
        return await self._schedule_repo.get_schedules_by_doctor_id(doctor_id)

    async def get_my_schedules(self, user_id: int) -> list[ScheduleEntity]:
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            raise ForbiddenException("User is not a doctor")
        return await self._schedule_repo.get_schedules_by_doctor_id(doctor.id)

    async def get_available_slots(
            self, doctor_id: int, date: datetime.date
    ) -> list[TimeSlotEntity]:
        day_of_week = date.weekday()

        schedule = await self._schedule_repo.get_schedule_by_doctor_and_day(doctor_id, day_of_week)
        if not schedule or not schedule.is_active:
            return []

        slots = []
        current_time = datetime.combine(date, schedule.start_time)
        end_datetime = datetime.combine(date, schedule.end_time)
        slot_duration = timedelta(minutes=schedule.slot_duration_minutes)

        while current_time + slot_duration <= end_datetime:
            slot_end = current_time + slot_duration
            slots.append(
                TimeSlotEntity(
                    start_time=current_time.time(),
                    end_time=slot_end.time(),
                    is_available=True,  # TODO: Check against appointments
                )
            )
            current_time = slot_end

        return slots

    async def delete_schedule(self, schedule_id: int, user_id: int) -> bool:
        existing = await self._schedule_repo.get_schedule_by_id(schedule_id)
        if not existing:
            raise NotFoundException("Schedule not found")

        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor or doctor.id != existing.doctor_id:
            raise ForbiddenException("Cannot delete another doctor's schedule")

        async with self._uow:
            return await self._schedule_repo.delete_schedule(schedule_id)

    def _validate_schedule(self, schedule: CreateScheduleDTO) -> None:
        if schedule.day_of_week < 0 or schedule.day_of_week > 6:
            raise BadRequestException("Day of week must be between 0 (Monday) and 6 (Sunday)")

        if schedule.start_time >= schedule.end_time:
            raise BadRequestException("Start time must be before end time")

        if schedule.slot_duration_minutes < 10 or schedule.slot_duration_minutes > 120:
            raise BadRequestException("Slot duration must be between 10 and 120 minutes")

    def _validate_schedule_update(
            self, existing: ScheduleEntity, update: UpdateScheduleDTO
    ) -> None:
        day_of_week = update.day_of_week if update.day_of_week is not None else existing.day_of_week
        start_time = update.start_time if update.start_time is not None else existing.start_time
        end_time = update.end_time if update.end_time is not None else existing.end_time
        slot_duration = (
            update.slot_duration_minutes
            if update.slot_duration_minutes is not None
            else existing.slot_duration_minutes
        )

        if day_of_week < 0 or day_of_week > 6:
            raise BadRequestException("Day of week must be between 0 (Monday) and 6 (Sunday)")

        if start_time >= end_time:
            raise BadRequestException("Start time must be before end time")

        if slot_duration < 10 or slot_duration > 120:
            raise BadRequestException("Slot duration must be between 10 and 120 minutes")
