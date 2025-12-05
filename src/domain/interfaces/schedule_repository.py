from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.schedules import ScheduleEntity, ScheduleWithDoctorEntity
from src.use_cases.schedules.dto import CreateScheduleDTO, UpdateScheduleDTO


class IScheduleRepository(ABC):
    @abstractmethod
    async def create_schedule(self, schedule: CreateScheduleDTO) -> ScheduleEntity:
        pass

    @abstractmethod
    async def update_schedule(self, schedule_id: int, schedule: UpdateScheduleDTO) -> ScheduleEntity:
        pass

    @abstractmethod
    async def get_schedule_by_id(self, schedule_id: int) -> Optional[ScheduleEntity]:
        pass

    @abstractmethod
    async def get_schedules_by_doctor_id(self, doctor_id: int) -> list[ScheduleEntity]:
        pass

    @abstractmethod
    async def get_schedule_by_doctor_and_day(
        self, doctor_id: int, day_of_week: int
    ) -> Optional[ScheduleEntity]:
        pass

    @abstractmethod
    async def get_active_schedules_by_doctor_id(self, doctor_id: int) -> list[ScheduleEntity]:
        pass

    @abstractmethod
    async def delete_schedule(self, schedule_id: int) -> bool:
        pass