from datetime import datetime
from typing import List, Optional

from sqlalchemy import insert, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.constants import ChatSessionStatus
from src.domain.entities.chat_messages import ChatMessageEntity
from src.domain.entities.chat_sessions import (
    ChatSessionEntity,
    ChatSessionWithMessagesEntity,
)
from src.domain.interfaces.chat_session_repository import IChatSessionRepository
from src.infrastructure.database.models.chat_sessions import ChatSession
from src.infrastructure.database.models.chat_messages import ChatMessage
from src.use_cases.chat.dto import CreateChatSessionDTO, UpdateChatSessionDTO


class ChatSessionRepository(IChatSessionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_session(self, session_dto: CreateChatSessionDTO) -> ChatSessionEntity:
        stmt = (
            insert(ChatSession)
            .values(**session_dto.to_payload(exclude_none=True))
            .returning(ChatSession)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_session(
        self, session_id: int, session_dto: UpdateChatSessionDTO
    ) -> ChatSessionEntity:
        stmt = (
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(**session_dto.to_payload(exclude_none=True))
            .returning(ChatSession)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_session_by_id(self, session_id: int) -> Optional[ChatSessionEntity]:
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_session_with_messages(
        self, session_id: int
    ) -> Optional[ChatSessionWithMessagesEntity]:
        stmt = (
            select(ChatSession)
            .options(joinedload(ChatSession.messages))
            .where(ChatSession.id == session_id)
        )
        result = await self._session.execute(stmt)
        # Need .unique() when using joinedload with collections
        obj = result.unique().scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm_with_messages(obj)

    async def get_sessions_by_user_id(
        self,
        user_id: int,
        status: Optional[ChatSessionStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ChatSessionEntity]:
        stmt = select(ChatSession).where(ChatSession.user_id == user_id)

        if status:
            stmt = stmt.where(ChatSession.status == status)

        stmt = stmt.order_by(ChatSession.created_at.desc()).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def close_session(self, session_id: int) -> ChatSessionEntity:
        stmt = (
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(status=ChatSessionStatus.CLOSED)
            .returning(ChatSession)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def delete_session(self, session_id: int) -> bool:
        stmt = delete(ChatSession).where(ChatSession.id == session_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def count_sessions_by_user_id(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(ChatSession)
            .where(ChatSession.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    def _from_orm(obj: ChatSession) -> ChatSessionEntity:
        return ChatSessionEntity(
            id=obj.id,
            status=obj.status,
            source=obj.source,
            locale=obj.locale,
            last_message_at=obj.last_message_at,
            context_json=obj.context_json,
            user_id=obj.user_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    def _from_orm_message(obj: ChatMessage) -> ChatMessageEntity:
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

    @staticmethod
    def _from_orm_with_messages(obj: ChatSession) -> ChatSessionWithMessagesEntity:
        messages = [
            ChatSessionRepository._from_orm_message(msg)
            for msg in obj.messages
        ]
        return ChatSessionWithMessagesEntity(
            id=obj.id,
            status=obj.status,
            source=obj.source,
            locale=obj.locale,
            last_message_at=obj.last_message_at,
            context_json=obj.context_json,
            user_id=obj.user_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            messages=messages,
        )
