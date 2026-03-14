from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.specializations import SpecializationEntity, SpecializationWithCountEntity
from src.use_cases.specializations.dto import CreateSpecializationDTO, UpdateSpecializationDTO


class ISpecializationRepository(ABC):
    @abstractmethod
    async def create_specialization(self, specialization: CreateSpecializationDTO) -> SpecializationEntity:
        pass

    @abstractmethod
    async def update_specialization(
        self, specialization_id: int, specialization: UpdateSpecializationDTO
    ) -> SpecializationEntity:
        pass

    @abstractmethod
    async def get_specialization_by_id(self, specialization_id: int) -> Optional[SpecializationEntity]:
        pass

    @abstractmethod
    async def get_specialization_by_title(self, title: str) -> Optional[SpecializationEntity]:
        pass

    @abstractmethod
    async def get_all_specializations(self) -> list[SpecializationEntity]:
        pass

    @abstractmethod
    async def get_all_specializations_with_count(self) -> list[SpecializationWithCountEntity]:
        pass

    @abstractmethod
    async def delete_specialization(self, specialization_id: int) -> bool:
        pass