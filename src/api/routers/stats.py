import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from api import schemas
from common import crud
from common import db

customers_router = APIRouter(prefix="/customers")


@customers_router.get("/{customer_id}/stats",
                      response_model=list[schemas.ResourceStatisticsByDaySchema])
async def stats_action(session: db.DatabaseDep,
                       customer_id: str,
                       from_date: Annotated[datetime.date, Query(alias='from')]):
    data = crud.get_statistics(
        session=session,
        customer_id=customer_id,
        from_date=from_date
    )
    return [
        schemas.ResourceStatisticsByDaySchema.model_validate(row) for row in data
    ]
