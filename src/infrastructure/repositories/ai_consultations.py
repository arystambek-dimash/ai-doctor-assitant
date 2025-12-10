from datetime import datetime

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ai_consultations import AIConsultationEntity, ChatMessageEntity
from src.domain.interfaces.ai_consultation_repository import IAIConsultationRepository
from src.infrastructure.database.models.ai_consultations import AIConsultation
from src.infrastructure.database.models.chat import ChatMessage
from src.use_cases.ai_consultations.dto import CreateConsultationDTO, UpdateConsultationDTO


class AIConsultationRepository(IAIConsultationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_consultation(self, consultation: CreateConsultationDTO) -> AIConsultationEntity:
        stmt = (
            insert(AIConsultation)
            .values(**consultation.to_payload(exclude_none=True))
            .returning(AIConsultation)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_consultation(
            self, consultation_id: int, consultation: UpdateConsultationDTO
    ) -> AIConsultationEntity:
        stmt = (
            update(AIConsultation)
            .where(AIConsultation.id == consultation_id)
            .values(**consultation.to_payload(exclude_none=True))
            .returning(AIConsultation)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_consultation_by_id(self, consultation_id: int) -> AIConsultationEntity | None:
        stmt = select(AIConsultation).where(AIConsultation.id == consultation_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_consultations_by_patient_id(
            self, patient_id: int, skip: int = 0, limit: int = 20
    ) -> list[AIConsultationEntity]:
        stmt = (
            select(AIConsultation)
            .where(AIConsultation.patient_id == patient_id)
            .order_by(AIConsultation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def add_message(
            self, consultation_id: int, role: str, content: str
    ) -> ChatMessageEntity:
        stmt = (
            insert(ChatMessage)
            .values(
                consultation_id=consultation_id,
                role=role,
                content=content,
                created_at=datetime.utcnow(),
            )
            .returning(ChatMessage)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._message_from_orm(obj)

    async def get_messages_by_consultation_id(
            self, consultation_id: int
    ) -> list[ChatMessageEntity]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.consultation_id == consultation_id)
            .order_by(ChatMessage.created_at)
        )
        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._message_from_orm(obj) for obj in objects]

    async def delete_consultation(self, consultation_id: int) -> bool:
        stmt = delete(AIConsultation).where(AIConsultation.id == consultation_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    def _from_orm(obj: AIConsultation) -> AIConsultationEntity:
        return AIConsultationEntity(
            id=obj.id,
            symptoms_text=obj.symptoms_text,
            recommended_specialization=obj.recommended_specialization,
            confidence=obj.confidence,
            ai_response_raw=obj.ai_response_raw,
            created_at=obj.created_at,
            patient_id=obj.patient_id,
            status=obj.status,
        )

    @staticmethod
    def _message_from_orm(obj: ChatMessage) -> ChatMessageEntity:
        return ChatMessageEntity(
            id=obj.id,
            consultation_id=obj.consultation_id,
            role=obj.role,
            content=obj.content,
            created_at=obj.created_at,
        )
