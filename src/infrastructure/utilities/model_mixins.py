from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import func


class TimeStampMixin:
    created_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), default=func.now())
    updated_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), default=func.now(), onupdate=func.now())
