from datetime import datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import IdMixin, TimeStampMixin
from ..core import Base


class MedicalRecord(Base, IdMixin):
    __tablename__ = "medical_records"

    diagnosis: orm.Mapped[str] = orm.mapped_column(sa.Text)
    prescription: orm.Mapped[Optional[str]] = orm.mapped_column(sa.Text, nullable=True)
    notes: orm.Mapped[Optional[str]] = orm.mapped_column(sa.Text, nullable=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, default=datetime.utcnow)

    patient_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    doctor_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("doctors.id", ondelete="CASCADE")
    )
    appointment_id: orm.Mapped[Optional[int]] = orm.mapped_column(
        sa.ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True,
        unique=True
    )

    patient = orm.relationship("User", back_populates="medical_records")
    doctor = orm.relationship("Doctor")
    appointment = orm.relationship(
        "Appointment",
        back_populates="medical_record"
    )
