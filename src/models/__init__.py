import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import String, Date, BigInteger, Float, create_engine, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

from src.common.settings import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DatabaseDep = Annotated[Session, Depends(get_db)]


class Base(DeclarativeBase):
    pass


class ResourceStatisticsByDay(Base):
    __tablename__ = "resource_statistics_by_day"
    __table__args__ = (
        PrimaryKeyConstraint("customer_id", "date"),
    )

    customer_id: Mapped[str] = mapped_column(String(length=255), primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date(), primary_key=True)

    success_requests: Mapped[int] = mapped_column(BigInteger())
    failed_requests: Mapped[int] = mapped_column(BigInteger())

    duration_mean: Mapped[float] = mapped_column(Float())
    duration_p50: Mapped[float] = mapped_column(Float())
    duration_p99: Mapped[float] = mapped_column(Float())
