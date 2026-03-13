from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.constants import MessageRole, ContentType


@dataclass(frozen=True)
class ChatMessageEntity:
    id: int
    role: MessageRole
    content: str
    content_type: ContentType
    model_name: Optional[str]
    prompt_version: Optional[str]
    token_input: Optional[int]
    token_output: Optional[int]
    latency_ms: Optional[int]
    session_id: int
    created_at: datetime
