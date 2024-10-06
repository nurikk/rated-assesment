import datetime

import sqlalchemy
from sqlalchemy import orm


class Base(orm.DeclarativeBase):
    pass


class ResourceStatisticsByDay(Base):
    __tablename__ = "resource_statistics_by_day"
    __table__args__ = (
        sqlalchemy.PrimaryKeyConstraint("customer_id", "date"),
    )

    customer_id: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(length=255), primary_key=True)
    date: orm.Mapped[datetime.date] = orm.mapped_column(sqlalchemy.Date(), primary_key=True)

    success_requests: orm.Mapped[int] = orm.mapped_column(sqlalchemy.BigInteger())
    failed_requests: orm.Mapped[int] = orm.mapped_column(sqlalchemy.BigInteger())

    duration_mean: orm.Mapped[float] = orm.mapped_column(sqlalchemy.Float())
    duration_p50: orm.Mapped[float] = orm.mapped_column(sqlalchemy.Float())
    duration_p99: orm.Mapped[float] = orm.mapped_column(sqlalchemy.Float())

    uptime_percentage: orm.Mapped[float] = orm.mapped_column(sqlalchemy.Float())
