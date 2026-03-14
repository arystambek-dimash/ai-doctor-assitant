from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import IdMixin, TimeStampMixin
from ..core import Base

if TYPE_CHECKING:
    from .doctors import Doctor
    from .triage_runs import TriageRun


class Specialization(Base, IdMixin, TimeStampMixin):
    __tablename__ = "specializations"

    title: orm.Mapped[str] = orm.mapped_column(
        sa.String(120),
        nullable=False,
        unique=True,
        index=True
    )
    slug: orm.Mapped[str] = orm.mapped_column(
        sa.String(120),
        nullable=False,
        unique=True,
        index=True
    )
    description: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.Text,
        nullable=True
    )
    is_active: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.true()
    )
    sort_order: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        nullable=False,
        server_default="0"
    )

    doctors: orm.Mapped[list["Doctor"]] = orm.relationship(
        "Doctor",
        back_populates="specialization"
    )
    triage_runs: orm.Mapped[list["TriageRun"]] = orm.relationship(
        "TriageRun",
        back_populates="recommended_specialization"
    )
