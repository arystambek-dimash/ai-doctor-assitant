from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import IdMixin
from ..core import Base


class ChatMessage(Base, IdMixin):
    __tablename__ = "chat_messages"

    consultation_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("ai_consultations.id", ondelete="CASCADE"),
        index=True
    )
    role: orm.Mapped[str] = orm.mapped_column(sa.String(20))  # user, assistant, system
    content: orm.Mapped[str] = orm.mapped_column(sa.Text)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, default=datetime.utcnow)

    consultation = orm.relationship("AIConsultation", back_populates="messages")