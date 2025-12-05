import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.domain.constants import DoctorStatus
from . import IdMixin, TimeStampMixin
from ..core import Base


class Doctor(Base, IdMixin, TimeStampMixin):
    __tablename__ = "doctors"

    bio: orm.Mapped[str] = orm.mapped_column(sa.Text)
    rating: orm.Mapped[float] = orm.mapped_column(sa.Float, default=5.0)
    experience_years: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)
    license_number: orm.Mapped[str] = orm.mapped_column(sa.String(100), unique=True)
    status: orm.Mapped[DoctorStatus] = orm.mapped_column(
        sa.Enum(DoctorStatus),
        default=DoctorStatus.PENDING
    )
    rejection_reason: orm.Mapped[str] = orm.mapped_column(sa.Text, nullable=True)

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )
    specialization_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("specializations.id", ondelete="CASCADE")
    )

    user = orm.relationship("User", back_populates="doctor_profile")
    specialization = orm.relationship("Specialization", back_populates="doctors")
    schedules = orm.relationship("Schedule", back_populates="doctor")
    appointments = orm.relationship("Appointment", back_populates="doctor")
