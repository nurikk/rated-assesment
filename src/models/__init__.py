import datetime

from sqlmodel import SQLModel, Field


class ResourceStatisticsByDay(SQLModel, table=True):
    __tablename__ = "resource_statistics_by_day"

    # id: int = Field(default=None, nullable=False, primary_key=True)

    dt: datetime.date = Field(default=None, nullable=False, primary_key=True)
    customer_id: str = Field(default=None, nullable=True, primary_key=True)
    request_path: str = Field(default=None, nullable=True, primary_key=True)
    status_code: int = Field(default=None, nullable=True, primary_key=True)

    duration_p50: float
    duration_p90: float
    duration_p95: float

