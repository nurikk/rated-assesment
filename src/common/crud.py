import datetime
from typing import Type

from sqlalchemy.orm import Session

from models import ResourceStatisticsByDay


def get_statistics(session: Session, customer_id: str, from_date: datetime.date) -> list[Type[ResourceStatisticsByDay]]:
    return session.query(ResourceStatisticsByDay).filter(
        ResourceStatisticsByDay.customer_id == customer_id,
        ResourceStatisticsByDay.date >= from_date
    ).all()
