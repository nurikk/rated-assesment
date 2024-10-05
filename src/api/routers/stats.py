import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from models import ResourceStatisticsByDay

# /customers/:id/stats?from=YYYY-MM-DD
customers_router = APIRouter(prefix="/customers")


@customers_router.get("/{customer_id}/stats", response_model=list[dict])
async def stats(customer_id: str, date_from: Annotated[datetime.date | None, Query(alias='from')] = None):
    qs = ResourceStatisticsByDay.filter(customer_id=customer_id, date__gte=date_from)
    return await ResourceStatisticsByDayPydantic.from_queryset(qs)
