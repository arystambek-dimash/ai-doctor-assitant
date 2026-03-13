from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

from src.domain.constants import TriageStatus, UrgencyLevel
from . import IdMixin
from ..core import Base

if TYPE_CHECKING:
    from .chat_sessions import ChatSession
    from .chat_messages import ChatMessage
    from .specializations import Specialization
    from .triage_candidates import TriageCandidate
    from .appointments import Appointment


class TriageRun(Base, IdMixin):
    __tablename__ = "triage_runs"

    status: orm.Mapped[TriageStatus] = orm.mapped_column(
        sa.Enum(
            TriageStatus,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="triagestatus"
        ),
        default=TriageStatus.SUCCESS
    )
    urgency: orm.Mapped[Optional[UrgencyLevel]] = orm.mapped_column(
        sa.Enum(
            UrgencyLevel,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="urgencylevel"
        ),
        nullable=True
    )
    confidence: orm.Mapped[Optional[float]] = orm.mapped_column(
        sa.Float,
        nullable=True
    )
    notes: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.Text,
        nullable=True
    )

    inputs_json: orm.Mapped[Optional[dict]] = orm.mapped_column(
        JSONB,
        nullable=True
    )
    outputs_json: orm.Mapped[Optional[dict]] = orm.mapped_column(
        JSONB,
        nullable=True
    )
    filters_json: orm.Mapped[Optional[dict]] = orm.mapped_column(
        JSONB,
        nullable=True
    )

    model_name: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.String(100),
        nullable=True
    )
    prompt_version: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.String(50),
        nullable=True
    )
    temperature: orm.Mapped[Optional[float]] = orm.mapped_column(
        sa.Float,
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
    error_message: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.Text,
        nullable=True
    )

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        default=func.now()
    )

    session_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    trigger_message_id: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.ForeignKey("chat_messages.id", ondelete="SET NULL"),
        nullable=True
    )
    recommended_specialization_id: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.ForeignKey("specializations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    session: orm.Mapped["ChatSession"] = orm.relationship(
        "ChatSession",
        back_populates="triage_runs"
    )
    trigger_message: orm.Mapped[Optional["ChatMessage"]] = orm.relationship(
        "ChatMessage",
        back_populates="triggered_triage_runs",
        foreign_keys=[trigger_message_id]
    )
    recommended_specialization: orm.Mapped[Optional["Specialization"]] = orm.relationship(
        "Specialization",
        back_populates="triage_runs"
    )
    candidates: orm.Mapped[list["TriageCandidate"]] = orm.relationship(
        "TriageCandidate",
        back_populates="triage_run",
        cascade="all, delete-orphan",
        order_by="TriageCandidate.rank"
    )
    appointments: orm.Mapped[list["Appointment"]] = orm.relationship(
        "Appointment",
        back_populates="triage_run"
    )

    __table_args__ = (
        sa.Index("ix_triage_runs_session_created", "session_id", "created_at"),
        sa.Index(
            "ix_triage_runs_specialization_created",
            "recommended_specialization_id",
            "created_at"
        ),
    )
