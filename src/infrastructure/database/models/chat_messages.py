from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import func

from src.domain.constants import MessageRole, ContentType
from . import IdMixin
from ..core import Base

if TYPE_CHECKING:
    from .chat_sessions import ChatSession
    from .triage_runs import TriageRun


class ChatMessage(Base, IdMixin):
    __tablename__ = "chat_messages"

    role: orm.Mapped[MessageRole] = orm.mapped_column(
        sa.Enum(
            MessageRole,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="messagerole"
        ),
        nullable=False
    )
    content: orm.Mapped[str] = orm.mapped_column(sa.Text, nullable=False)
    content_type: orm.Mapped[ContentType] = orm.mapped_column(
        sa.Enum(
            ContentType,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="contenttype"
        ),
        default=ContentType.TEXT
    )

    model_name: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.String(100),
        nullable=True
    )
    prompt_version: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.String(50),
        nullable=True
    )
    token_input: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.Integer,
        nullable=True
    )
    token_output: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.Integer,
        nullable=True
    )
    latency_ms: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.Integer,
        nullable=True
    )

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        default=func.now(),
        index=True
    )

    session_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    session: orm.Mapped["ChatSession"] = orm.relationship(
        "ChatSession",
        back_populates="messages"
    )
    triggered_triage_runs: orm.Mapped[list["TriageRun"]] = orm.relationship(
        "TriageRun",
        back_populates="trigger_message",
        foreign_keys="TriageRun.trigger_message_id"
    )

    __table_args__ = (
        sa.Index("ix_chat_messages_session_created", "session_id", "created_at"),
    )
