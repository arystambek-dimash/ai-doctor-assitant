from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import IdMixin, TimeStampMixin
from ..core import Base

if TYPE_CHECKING:
    from .doctors import Doctor
    from .appointments import Appointment
    from .medical_records import MedicalRecord
    from .chat_sessions import ChatSession


class User(Base, IdMixin, TimeStampMixin):
    __tablename__ = "users"

    email: orm.Mapped[str] = orm.mapped_column(sa.String(255), unique=True, index=True)
    full_name: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    phone: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(20), nullable=True)
    password_hash: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    is_admin: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)

    doctor_profile: orm.Mapped[Optional["Doctor"]] = orm.relationship(
        "Doctor",
        back_populates="user",
        uselist=False
    )
    appointments_as_patient: orm.Mapped[list["Appointment"]] = orm.relationship(
        "Appointment",
        back_populates="patient"
    )
    medical_records: orm.Mapped[list["MedicalRecord"]] = orm.relationship(
        "MedicalRecord",
        back_populates="patient"
    )
    chat_sessions: orm.Mapped[list["ChatSession"]] = orm.relationship(
        "ChatSession",
        back_populates="user"
    )

    @property
    def is_doctor(self) -> bool:
        from src.domain.constants import DoctorStatus
        return (
            self.doctor_profile is not None
            and self.doctor_profile.status == DoctorStatus.APPROVED
        )
