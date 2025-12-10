from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import IdMixin
from ..core import Base


class AIConsultation(Base, IdMixin):
    __tablename__ = "ai_consultations"

    symptoms_text: orm.Mapped[str] = orm.mapped_column(sa.Text)
    recommended_specialization: orm.Mapped[str | None] = orm.mapped_column(sa.String(100), nullable=True)
    confidence: orm.Mapped[float | None] = orm.mapped_column(sa.Float, nullable=True)
    ai_response_raw: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)  # Full JSON response
    status: orm.Mapped[str] = orm.mapped_column(sa.String(20), default="active")
    created_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, default=datetime.utcnow)

    patient_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )

    patient = orm.relationship("User", back_populates="ai_consultations")
    appointment = orm.relationship(
        "Appointment",
        back_populates="ai_consultation"
    )
    messages = orm.relationship("ChatMessage", back_populates="consultation", order_by="ChatMessage.created_at")
