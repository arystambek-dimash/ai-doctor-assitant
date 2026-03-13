from abc import ABC, abstractmethod
from typing import Optional

from src.domain.constants import ChatSessionStatus
from src.domain.entities.chat_sessions import (
    ChatSessionEntity,
    ChatSessionWithMessagesEntity,
)
from src.use_cases.chat.dto import CreateChatSessionDTO, UpdateChatSessionDTO


class IChatSessionRepository(ABC):
    @abstractmethod
    async def create_session(self, session: CreateChatSessionDTO) -> ChatSessionEntity:
        pass

    @abstractmethod
    async def update_session(
        self, session_id: int, session: UpdateChatSessionDTO
    ) -> ChatSessionEntity:
        pass

    @abstractmethod
    async def get_session_by_id(self, session_id: int) -> Optional[ChatSessionEntity]:
        pass

    @abstractmethod
    async def get_session_with_messages(
        self, session_id: int
    ) -> Optional[ChatSessionWithMessagesEntity]:
        pass

    @abstractmethod
    async def get_sessions_by_user_id(
        self,
        user_id: int,
        status: Optional[ChatSessionStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ChatSessionEntity]:
        pass

    @abstractmethod
    async def close_session(self, session_id: int) -> ChatSessionEntity:
        pass

    @abstractmethod
    async def delete_session(self, session_id: int) -> bool:
        pass
