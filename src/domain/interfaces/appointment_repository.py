from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional

from src.domain.constants import AppointmentStatus
from src.domain.entities.appointments import AppointmentEntity, AppointmentWithDetailsEntity
from src.use_cases.appointments.dto import CreateAppointmentDTO, UpdateAppointmentDTO


class IAppointmentRepository(ABC):
    @abstractmethod
    async def create_appointment(self, appointment: CreateAppointmentDTO) -> AppointmentEntity:
        pass

    @abstractmethod
    async def update_appointment(
        self, appointment_id: int, appointment: UpdateAppointmentDTO
    ) -> AppointmentEntity:
        pass

    @abstractmethod
    async def get_appointment_by_id(self, appointment_id: int) -> Optional[AppointmentEntity]:
        pass

    @abstractmethod
    async def get_appointment_with_details(
        self, appointment_id: int
    ) -> Optional[AppointmentWithDetailsEntity]:
        pass

    @abstractmethod
    async def get_appointments_by_patient_id(
        self,
        patient_id: int,
        status: Optional[AppointmentStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AppointmentWithDetailsEntity]:
        pass

    @abstractmethod
    async def get_appointments_by_doctor_id(
        self,
        doctor_id: int,
        status: Optional[AppointmentStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AppointmentWithDetailsEntity]:
        pass

    @abstractmethod
    async def get_doctor_appointments_for_date(
        self, doctor_id: int, target_date: date
    ) -> list[AppointmentEntity]:
        pass

    @abstractmethod
    async def check_slot_availability(
        self, doctor_id: int, date_time: datetime, duration_minutes: int = 30
    ) -> bool:
        pass

    @abstractmethod
    async def delete_appointment(self, appointment_id: int) -> bool:
        pass