from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.dialects.postgresql import JSONB

from src.domain.constants import ChatSessionStatus, ChatSource
from . import IdMixin, TimeStampMixin
from ..core import Base

if TYPE_CHECKING:
    from .users import User
    from .chat_messages import ChatMessage
    from .triage_runs import TriageRun


class ChatSession(Base, IdMixin, TimeStampMixin):
    __tablename__ = "chat_sessions"

    status: orm.Mapped[ChatSessionStatus] = orm.mapped_column(
        sa.Enum(
            ChatSessionStatus,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="chatsessionstatus"
        ),
        default=ChatSessionStatus.ACTIVE,
        index=True
    )
    source: orm.Mapped[ChatSource] = orm.mapped_column(
        sa.Enum(
            ChatSource,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="chatsource"
        ),
        default=ChatSource.WEB
    )
    locale: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.String(10),
        nullable=True,
        default="ru"
    )
    last_message_at: orm.Mapped[Optional[datetime]] = orm.mapped_column(
        sa.DateTime(timezone=True),
        nullable=True
    )
    context_json: orm.Mapped[Optional[dict]] = orm.mapped_column(
        JSONB,
        nullable=True
    )

    user_id: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    user: orm.Mapped[Optional["User"]] = orm.relationship(
        "User",
        back_populates="chat_sessions"
    )
    messages: orm.Mapped[list["ChatMessage"]] = orm.relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )
    triage_runs: orm.Mapped[list["TriageRun"]] = orm.relationship(
        "TriageRun",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        sa.Index("ix_chat_sessions_user_created", "user_id", "created_at"),
        sa.Index("ix_chat_sessions_status_updated", "status", "updated_at"),
    )
