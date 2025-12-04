from datetime import datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.domain.constants import AppointmentStatus
from src.domain.model_mixins import IdMixin, TimeStampMixin
from ..core import Base


class Appointment(Base, IdMixin, TimeStampMixin):
    __tablename__ = "appointments"

    date_time: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, index=True)
    status: orm.Mapped[AppointmentStatus] = orm.mapped_column(
        sa.Enum(AppointmentStatus),
        default=AppointmentStatus.SCHEDULED
    )
    notes: orm.Mapped[Optional[str]] = orm.mapped_column(sa.Text, nullable=True)

    patient_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    doctor_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("doctors.id", ondelete="CASCADE")
    )
    ai_consultation_id: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.ForeignKey("ai_consultations.id", ondelete="SET NULL"),
        nullable=True
    )

    patient = orm.relationship(
        "User",
        back_populates="appointments_as_patient",
        foreign_keys=[patient_id]
    )
    doctor = orm.relationship("Doctor", back_populates="appointments")
    ai_consultation = orm.relationship(
        "AIConsultation",
        back_populates="appointment"
    )
    medical_record = orm.relationship(
        "MedicalRecord",
        back_populates="appointment"
    )
