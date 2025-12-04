from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.domain.model_mixins import IdMixin
from ..core import Base


class AIConsultation(Base, IdMixin):
    __tablename__ = "ai_consultations"

    symptoms_text: orm.Mapped[str] = orm.mapped_column(sa.Text)
    recommended_specialization: orm.Mapped[str] = orm.mapped_column(sa.String(100))
    confidence: orm.Mapped[float] = orm.mapped_column(sa.Float)
    ai_response_raw: orm.Mapped[str] = orm.mapped_column(sa.Text)  # Full JSON response
    created_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, default=datetime.utcnow)

    patient_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )

    patient = orm.relationship("User", back_populates="ai_consultations")
    appointment = orm.relationship(
        "Appointment",
        back_populates="ai_consultation"
    )
