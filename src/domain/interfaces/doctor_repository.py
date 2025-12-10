from abc import ABC, abstractmethod
from typing import Optional

from src.domain.constants import DoctorStatus
from src.domain.entities.doctors import DoctorEntity, DoctorWithDetailsEntity
from src.use_cases.doctors.dto import CreateDoctorDTO, UpdateDoctorDTO


class IDoctorRepository(ABC):
    @abstractmethod
    async def create_doctor(self, doctor: CreateDoctorDTO) -> DoctorEntity:
        pass

    @abstractmethod
    async def update_doctor(self, doctor_id: int, doctor: UpdateDoctorDTO) -> DoctorEntity:
        pass

    @abstractmethod
    async def get_doctor_by_id(self, doctor_id: int) -> Optional[DoctorEntity]:
        pass

    @abstractmethod
    async def get_doctor_by_user_id(self, user_id: int) -> Optional[DoctorEntity]:
        pass

    @abstractmethod
    async def get_doctor_by_license_number(self, license_number: str) -> Optional[DoctorEntity]:
        pass

    @abstractmethod
    async def get_doctor_with_details(self, doctor_id: int) -> Optional[DoctorWithDetailsEntity]:
        pass

    @abstractmethod
    async def get_all_doctors(
            self,
            specialization_id: Optional[int] = None,
            status: Optional[DoctorStatus] = None,
            skip: int = 0,
            limit: int = 10,
    ) -> list[DoctorWithDetailsEntity]:
        pass

    @abstractmethod
    async def delete_doctor(self, doctor_id: int) -> bool:
        pass

    @abstractmethod
    async def get_doctors_by_specialization(self, specialization_id: int) -> list[DoctorWithDetailsEntity]:
        pass
