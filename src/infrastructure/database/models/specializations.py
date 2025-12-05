import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import IdMixin, TimeStampMixin
from ..core import Base


class Specialization(Base, IdMixin):
    __tablename__ = "specializations"

    title: orm.Mapped[str] = orm.mapped_column(sa.String)
    description: orm.Mapped[str] = orm.mapped_column(sa.String)

    doctors = orm.relationship("Doctor", back_populates="specialization")
