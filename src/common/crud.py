import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import ResourceStatisticsByDay


async def get_statistics(session: AsyncSession,
                         customer_id: str,
                         from_date: datetime.date) -> Sequence[ResourceStatisticsByDay]:
    query = select(ResourceStatisticsByDay).filter(
        ResourceStatisticsByDay.customer_id == customer_id,
        ResourceStatisticsByDay.date >= from_date
    )
    data = await session.execute(query)
    return data.scalars().all()
