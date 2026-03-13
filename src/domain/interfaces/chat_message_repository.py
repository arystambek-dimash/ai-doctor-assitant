from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.chat_messages import ChatMessageEntity
from src.use_cases.chat.dto import CreateChatMessageDTO


class IChatMessageRepository(ABC):
    @abstractmethod
    async def create_message(self, message: CreateChatMessageDTO) -> ChatMessageEntity:
        pass

    @abstractmethod
    async def get_message_by_id(self, message_id: int) -> Optional[ChatMessageEntity]:
        pass

    @abstractmethod
    async def get_messages_by_session_id(
        self,
        session_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ChatMessageEntity]:
        pass

    @abstractmethod
    async def count_messages_by_session_id(self, session_id: int) -> int:
        pass
