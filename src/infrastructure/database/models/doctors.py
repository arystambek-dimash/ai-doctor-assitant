from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.domain.constants import DoctorStatus
from . import IdMixin, TimeStampMixin
from ..core import Base

if TYPE_CHECKING:
    from .users import User
    from .specializations import Specialization
    from .schedules import Schedule
    from .appointments import Appointment
    from .triage_candidates import TriageCandidate


class Doctor(Base, IdMixin, TimeStampMixin):
    __tablename__ = "doctors"

    bio: orm.Mapped[str] = orm.mapped_column(sa.Text)
    rating: orm.Mapped[float] = orm.mapped_column(sa.Float, default=5.0)
    experience_years: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)
    license_number: orm.Mapped[str] = orm.mapped_column(sa.String(100), unique=True)
    status: orm.Mapped[DoctorStatus] = orm.mapped_column(
        sa.Enum(
            DoctorStatus,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="doctorstatus"
        ),
        default=DoctorStatus.PENDING
    )
    rejection_reason: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.Text,
        nullable=True
    )
    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )
    specialization_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("specializations.id", ondelete="CASCADE")
    )

    user: orm.Mapped["User"] = orm.relationship(
        "User",
        back_populates="doctor_profile"
    )
    specialization: orm.Mapped["Specialization"] = orm.relationship(
        "Specialization",
        back_populates="doctors"
    )
    schedules: orm.Mapped[list["Schedule"]] = orm.relationship(
        "Schedule",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )
    appointments: orm.Mapped[list["Appointment"]] = orm.relationship(
        "Appointment",
        back_populates="doctor"
    )
    triage_candidates: orm.Mapped[list["TriageCandidate"]] = orm.relationship(
        "TriageCandidate",
        back_populates="doctor"
    )
