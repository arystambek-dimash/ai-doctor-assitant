from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.constants import (
    ChatSessionStatus,
    ChatSource,
    MessageRole,
    ContentType,
)
from src.infrastructure.utilities.dto import BaseDTOMixin


@dataclass
class CreateChatSessionDTO(BaseDTOMixin):
    user_id: Optional[int] = None
    source: ChatSource = ChatSource.WEB
    locale: Optional[str] = "ru"
    context_json: Optional[dict] = None


@dataclass
class UpdateChatSessionDTO(BaseDTOMixin):
    status: Optional[ChatSessionStatus] = None
    last_message_at: Optional[datetime] = None
    context_json: Optional[dict] = None


@dataclass
class CreateChatMessageDTO(BaseDTOMixin):
    session_id: int
    role: MessageRole
    content: str
    content_type: ContentType = ContentType.TEXT
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    token_input: Optional[int] = None
    token_output: Optional[int] = None
    latency_ms: Optional[int] = None
