from datetime import datetime
from typing import List, Optional

from src.domain.constants import (
    ChatSessionStatus,
    ChatSource,
    MessageRole,
    ContentType,
)
from src.domain.entities.chat_messages import ChatMessageEntity
from src.domain.entities.chat_sessions import (
    ChatSessionEntity,
    ChatSessionWithMessagesEntity,
)
from src.domain.errors import BadRequestException, NotFoundException, ForbiddenException
from src.domain.interfaces.chat_message_repository import IChatMessageRepository
from src.domain.interfaces.chat_session_repository import IChatSessionRepository
from src.domain.interfaces.uow import IUoW
from src.use_cases.chat.dto import (
    CreateChatSessionDTO,
    UpdateChatSessionDTO,
    CreateChatMessageDTO,
)


class ChatUseCase:
    def __init__(
        self,
        uow: IUoW,
        chat_session_repository: IChatSessionRepository,
        chat_message_repository: IChatMessageRepository,
    ):
        self._uow = uow
        self._session_repo = chat_session_repository
        self._message_repo = chat_message_repository

    async def create_session(
        self,
        user_id: Optional[int] = None,
        source: ChatSource = ChatSource.WEB,
        locale: Optional[str] = "ru",
        context_json: Optional[dict] = None,
    ) -> ChatSessionEntity:
        dto = CreateChatSessionDTO(
            user_id=user_id,
            source=source,
            locale=locale,
            context_json=context_json,
        )

        async with self._uow:
            session = await self._session_repo.create_session(dto)
        return session

    async def get_session_by_id(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> ChatSessionEntity:
        session = await self._session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        return session

    async def get_session_with_messages(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> ChatSessionWithMessagesEntity:
        session = await self._session_repo.get_session_with_messages(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        return session

    async def get_my_sessions(
        self,
        user_id: int,
        status: Optional[ChatSessionStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ChatSessionEntity]:
        return await self._session_repo.get_sessions_by_user_id(
            user_id, status=status, skip=skip, limit=limit
        )

    async def close_session(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> ChatSessionEntity:
        session = await self._session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        if session.status == ChatSessionStatus.CLOSED:
            raise BadRequestException("Session is already closed")

        async with self._uow:
            updated = await self._session_repo.close_session(session_id)
        return updated

    async def send_message(
        self,
        session_id: int,
        content: str,
        role: MessageRole = MessageRole.USER,
        content_type: ContentType = ContentType.TEXT,
        user_id: Optional[int] = None,
        is_admin: bool = False,
        model_name: Optional[str] = None,
        prompt_version: Optional[str] = None,
        token_input: Optional[int] = None,
        token_output: Optional[int] = None,
        latency_ms: Optional[int] = None,
    ) -> ChatMessageEntity:
        session = await self._session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        if session.status == ChatSessionStatus.CLOSED:
            raise BadRequestException("Cannot send messages to a closed session")

        if not content.strip():
            raise BadRequestException("Message content cannot be empty")

        message_dto = CreateChatMessageDTO(
            session_id=session_id,
            role=role,
            content=content,
            content_type=content_type,
            model_name=model_name,
            prompt_version=prompt_version,
            token_input=token_input,
            token_output=token_output,
            latency_ms=latency_ms,
        )

        async with self._uow:
            message = await self._message_repo.create_message(message_dto)
            await self._session_repo.update_session(
                session_id,
                UpdateChatSessionDTO(last_message_at=datetime.now()),
            )

        return message

    async def get_messages(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatMessageEntity]:
        session = await self._session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        return await self._message_repo.get_messages_by_session_id(
            session_id, skip=skip, limit=limit
        )

    async def delete_session(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> bool:
        session = await self._session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Chat session not found")

        if not is_admin and session.user_id and session.user_id != user_id:
            raise ForbiddenException("Access denied")

        async with self._uow:
            return await self._session_repo.delete_session(session_id)
