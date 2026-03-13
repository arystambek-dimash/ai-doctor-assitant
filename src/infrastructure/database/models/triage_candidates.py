from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.dialects.postgresql import JSONB

from . import IdMixin
from ..core import Base

if TYPE_CHECKING:
    from .triage_runs import TriageRun
    from .doctors import Doctor


class TriageCandidate(Base, IdMixin):
    __tablename__ = "triage_candidates"

    rank: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)
    score: orm.Mapped[float] = orm.mapped_column(sa.Float, nullable=False)
    reason: orm.Mapped[Optional[str]] = orm.mapped_column(sa.Text, nullable=True)
    matched_filters_json: orm.Mapped[Optional[dict]] = orm.mapped_column(
        JSONB,
        nullable=True
    )

    triage_run_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("triage_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    doctor_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("doctors.id", ondelete="RESTRICT"),
        nullable=False
    )

    triage_run: orm.Mapped["TriageRun"] = orm.relationship(
        "TriageRun",
        back_populates="candidates"
    )
    doctor: orm.Mapped["Doctor"] = orm.relationship(
        "Doctor",
        back_populates="triage_candidates"
    )

    __table_args__ = (
        sa.UniqueConstraint("triage_run_id", "rank", name="uq_triage_candidate_run_rank"),
        sa.UniqueConstraint("triage_run_id", "doctor_id", name="uq_triage_candidate_run_doctor"),
        sa.Index("ix_triage_candidates_run_rank", "triage_run_id", "rank"),
    )
