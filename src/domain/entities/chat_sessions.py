from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from src.domain.constants import ChatSessionStatus, ChatSource

if TYPE_CHECKING:
    from src.domain.entities.chat_messages import ChatMessageEntity


@dataclass(frozen=True)
class ChatSessionEntity:
    id: int
    status: ChatSessionStatus
    source: ChatSource
    locale: Optional[str]
    last_message_at: Optional[datetime]
    context_json: Optional[dict]
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ChatSessionWithMessagesEntity:
    id: int
    status: ChatSessionStatus
    source: ChatSource
    locale: Optional[str]
    last_message_at: Optional[datetime]
    context_json: Optional[dict]
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    messages: list
