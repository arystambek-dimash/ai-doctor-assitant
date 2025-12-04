from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm


class TimeStampMixin:
    created_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, default=sa.func.now())
    updated_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())


class IdMixin:
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
