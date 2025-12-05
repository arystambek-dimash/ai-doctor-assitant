from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.ai_consultations import AIConsultationEntity, ChatMessageEntity
from src.use_cases.ai_consultations.dto import CreateConsultationDTO, UpdateConsultationDTO


class IAIConsultationRepository(ABC):
    @abstractmethod
    async def create_consultation(self, consultation: CreateConsultationDTO) -> AIConsultationEntity:
        pass

    @abstractmethod
    async def update_consultation(
            self, consultation_id: int, consultation: UpdateConsultationDTO
    ) -> AIConsultationEntity:
        pass

    @abstractmethod
    async def get_consultation_by_id(self, consultation_id: int) -> Optional[AIConsultationEntity]:
        pass

    @abstractmethod
    async def get_consultations_by_patient_id(
            self, patient_id: int, skip: int = 0, limit: int = 20
    ) -> list[AIConsultationEntity]:
        pass

    @abstractmethod
    async def add_message(
            self, consultation_id: int, role: str, content: str
    ) -> ChatMessageEntity:
        pass

    @abstractmethod
    async def get_messages_by_consultation_id(
            self, consultation_id: int
    ) -> list[ChatMessageEntity]:
        pass

    @abstractmethod
    async def delete_consultation(self, consultation_id: int) -> bool:
        pass
