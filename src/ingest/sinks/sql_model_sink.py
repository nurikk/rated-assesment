import asyncio

from bytewax.outputs import DynamicSink, StatelessSinkPartition
from sqlalchemy.orm import Session
from tortoise import Model
from tortoise.transactions import in_transaction

from src.models import Base, engine
from src.common import db
from sqlalchemy.dialects.postgresql import insert

class TortoiseClient:
    def __init__(self, model_cls: type[Model]):
        self.inited = False
        self.model_cls = model_cls

    async def send(self, batch: list[dict]) -> None:
        if not self.inited:
            await db.init()
            self.inited = True
        async with in_transaction() as tx_ctx:
            await self.model_cls.bulk_create(
                objects=[self.model_cls(**record) for record in batch],
                on_conflict=['customer_id', 'date'],
                update_fields=['success_requests', 'failed_requests',
                               'duration_mean', 'duration_p50', 'duration_p99'],
                using_db=tx_ctx)


class SqlModelPartition(StatelessSinkPartition):
    def __init__(self, model_cls: type[Base]):
        self.model_cls = model_cls

    def write_batch(self, batch: list) -> None:
        with Session(engine) as session:

            stmt = insert(self.model_cls).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=[
                    'customer_id',
                    'date'
                ],
                set_=dict(
                    success_requests=stmt.excluded.success_requests,
                    failed_requests=stmt.excluded.failed_requests,
                    duration_mean=stmt.excluded.duration_mean,
                    duration_p50=stmt.excluded.duration_p50,
                    duration_p99=stmt.excluded.duration_p99,
                )
            )
            session.execute(stmt)
            session.commit()


class SqlModelSink(DynamicSink):
    def __init__(self, model_cls: type[Base]):
        self.model_cls = model_cls

    def build(self, step_id: str, worker_index: int, worker_count: int):
        return SqlModelPartition(model_cls=self.model_cls)
