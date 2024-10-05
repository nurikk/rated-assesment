import datetime

import pydantic


class ResourceStatisticsByDaySchema(pydantic.BaseModel):
    customer_id: str
    date: datetime.date

    success_requests: int
    failed_requests: int

    duration_mean: float
    duration_p50: float
    duration_p99: float

    class Config:
        from_attributes = True
