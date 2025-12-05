from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import IdMixin, TimeStampMixin
from ..core import Base


class User(Base, IdMixin, TimeStampMixin):
    __tablename__ = "users"

    email: orm.Mapped[str] = orm.mapped_column(sa.String(255), unique=True, index=True)
    password_hash: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    full_name: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    phone: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(20), nullable=True)
    is_admin: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)

    doctor_profile = orm.relationship("Doctor", back_populates="user")
    ai_consultations = orm.relationship("AIConsultation", back_populates="patient")
    appointments_as_patient = orm.relationship("Appointment", back_populates="patient")
    medical_records = orm.relationship("MedicalRecord", back_populates="patient")

    @property
    def is_doctor(self) -> bool:
        return self.doctor_profile is not None
