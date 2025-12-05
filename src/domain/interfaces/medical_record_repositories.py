from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.medical_records import MedicalRecordEntity, MedicalRecordWithDetailsEntity
from src.use_cases.medical_records.dto import CreateMedicalRecordDTO, UpdateMedicalRecordDTO


class IMedicalRecordRepository(ABC):
    @abstractmethod
    async def create_medical_record(self, record: CreateMedicalRecordDTO) -> MedicalRecordEntity:
        pass

    @abstractmethod
    async def update_medical_record(
        self, record_id: int, record: UpdateMedicalRecordDTO
    ) -> MedicalRecordEntity:
        pass

    @abstractmethod
    async def get_medical_record_by_id(self, record_id: int) -> Optional[MedicalRecordEntity]:
        pass

    @abstractmethod
    async def get_medical_record_with_details(
        self, record_id: int
    ) -> Optional[MedicalRecordWithDetailsEntity]:
        pass

    @abstractmethod
    async def get_medical_records_by_patient_id(
        self, patient_id: int, skip: int = 0, limit: int = 20
    ) -> list[MedicalRecordWithDetailsEntity]:
        pass

    @abstractmethod
    async def get_medical_records_by_doctor_id(
        self, doctor_id: int, skip: int = 0, limit: int = 20
    ) -> list[MedicalRecordWithDetailsEntity]:
        pass

    @abstractmethod
    async def get_medical_record_by_appointment_id(
        self, appointment_id: int
    ) -> Optional[MedicalRecordEntity]:
        pass

    @abstractmethod
    async def delete_medical_record(self, record_id: int) -> bool:
        pass