import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.domain.model_mixins import IdMixin
from ..core import Base


class Specialization(Base, IdMixin):
    __tablename__ = "specializations"

    title: orm.Mapped[str] = orm.mapped_column(sa.String)
    description: orm.Mapped[str] = orm.mapped_column(sa.String)
