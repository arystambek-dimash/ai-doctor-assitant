import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.domain.constants import DoctorStatus
from src.infrastructure.database.core import Base
from src.infrastructure.utilities.model_mixins import TimeStampMixin, IdMixin


class DoctorApplications(Base, IdMixin, TimeStampMixin):
    __tablename__ = "doctor_applications"

    status: orm.Mapped[DoctorStatus] = orm.mapped_column(
        sa.Enum(DoctorStatus),
        default=DoctorStatus.PENDING
    )
    bio: orm.Mapped[str] = orm.mapped_column(sa.Text)
