from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.domain.constants import AppointmentStatus, VisitType
from . import IdMixin, TimeStampMixin
from ..core import Base

if TYPE_CHECKING:
    from .users import User
    from .doctors import Doctor
    from .triage_runs import TriageRun
    from .medical_records import MedicalRecord


class Appointment(Base, IdMixin, TimeStampMixin):
    __tablename__ = "appointments"

    date_time: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        index=True
    )
    status: orm.Mapped[AppointmentStatus] = orm.mapped_column(
        sa.Enum(
            AppointmentStatus,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="appointmentstatus"
        ),
        default=AppointmentStatus.SCHEDULED
    )
    duration_minutes: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        default=30
    )
    visit_type: orm.Mapped[VisitType] = orm.mapped_column(
        sa.Enum(
            VisitType,
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
            name="visittype"
        ),
        default=VisitType.OFFLINE
    )
    notes: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.Text,
        nullable=True
    )
    cancel_reason: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.Text,
        nullable=True
    )

    patient_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    doctor_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("doctors.id", ondelete="RESTRICT")
    )
    triage_run_id: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.ForeignKey("triage_runs.id", ondelete="SET NULL"),
        nullable=True
    )
    rescheduled_from_id: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True
    )

    patient: orm.Mapped["User"] = orm.relationship(
        "User",
        back_populates="appointments_as_patient",
        foreign_keys=[patient_id]
    )
    doctor: orm.Mapped["Doctor"] = orm.relationship(
        "Doctor",
        back_populates="appointments"
    )
    triage_run: orm.Mapped[Optional["TriageRun"]] = orm.relationship(
        "TriageRun",
        back_populates="appointments"
    )
    rescheduled_from: orm.Mapped[Optional["Appointment"]] = orm.relationship(
        "Appointment",
        remote_side="Appointment.id",
        foreign_keys=[rescheduled_from_id],
        backref=orm.backref("rescheduled_to", uselist=False)
    )
    medical_record: orm.Mapped[Optional["MedicalRecord"]] = orm.relationship(
        "MedicalRecord",
        back_populates="appointment",
        uselist=False
    )

    __table_args__ = (
        sa.Index(
            "ix_appointments_doctor_datetime_active",
            "doctor_id",
            "date_time",
            postgresql_where=sa.text(
                "status IN ('scheduled', 'confirmed')"
            )
        ),
    )
