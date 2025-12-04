from datetime import time

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.domain.model_mixins import IdMixin
from ..core import Base


class Schedule(Base, IdMixin):
    __tablename__ = "schedules"

    day_of_week: orm.Mapped[int] = orm.mapped_column(sa.Integer)  # 0=Monday, 6=Sunday
    start_time: orm.Mapped[time] = orm.mapped_column(sa.Time)
    end_time: orm.Mapped[time] = orm.mapped_column(sa.Time)
    slot_duration_minutes: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=30)
    is_active: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=True)

    doctor_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("doctors.id", ondelete="CASCADE")
    )

    doctor = orm.relationship("Doctor", back_populates="schedules")
