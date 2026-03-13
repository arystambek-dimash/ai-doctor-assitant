from typing import List, Optional

from sqlalchemy import insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.chat_messages import ChatMessageEntity
from src.domain.interfaces.chat_message_repository import IChatMessageRepository
from src.infrastructure.database.models.chat_messages import ChatMessage
from src.use_cases.chat.dto import CreateChatMessageDTO


class ChatMessageRepository(IChatMessageRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_message(self, message: CreateChatMessageDTO) -> ChatMessageEntity:
        stmt = (
            insert(ChatMessage)
            .values(**message.to_payload(exclude_none=True))
            .returning(ChatMessage)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_message_by_id(self, message_id: int) -> Optional[ChatMessageEntity]:
        stmt = select(ChatMessage).where(ChatMessage.id == message_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_messages_by_session_id(
        self,
        session_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatMessageEntity]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def count_messages_by_session_id(self, session_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.session_id == session_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    def _from_orm(obj: ChatMessage) -> ChatMessageEntity:
        return ChatMessageEntity(
            id=obj.id,
            role=obj.role,
            content=obj.content,
            content_type=obj.content_type,
            model_name=obj.model_name,
            prompt_version=obj.prompt_version,
            token_input=obj.token_input,
            token_output=obj.token_output,
            latency_ms=obj.latency_ms,
            session_id=obj.session_id,
            created_at=obj.created_at,
        )
