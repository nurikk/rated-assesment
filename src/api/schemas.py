import datetime

import pydantic
from pydantic import ConfigDict


class ResourceStatisticsByDaySchema(pydantic.BaseModel):
    customer_id: str
    date: datetime.date

    success_requests: int
    failed_requests: int

    duration_mean: float
    duration_p50: float
    duration_p99: float

    uptime_percentage: float

    model_config = ConfigDict(from_attributes=True)

