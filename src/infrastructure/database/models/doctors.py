import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import IdMixin
from ..core import Base


class Doctor(Base, IdMixin):
    __tablename__ = "doctors"

    bio: orm.Mapped[str] = orm.mapped_column(sa.Text)
    rating: orm.Mapped[float] = orm.mapped_column(sa.Float, default=5.0)
    experience_years: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)

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
