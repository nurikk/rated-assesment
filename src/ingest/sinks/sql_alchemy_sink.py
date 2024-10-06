from bytewax.outputs import DynamicSink, StatelessSinkPartition
from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models import Base


class SqlAlchemyPartition(StatelessSinkPartition):
    def __init__(self, model_cls: type[Base],
                 index_elements: list[str],
                 set_elements: list[str],
                 session: Session):
        self.model_cls = model_cls
        self.index_elements = index_elements
        self.set_elements = set_elements
        self.session = session

    def write_batch(self, batch: list) -> None:
        stmt = insert(self.model_cls).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=self.index_elements,
            set_={set_el: stmt.excluded[set_el] for set_el in self.set_elements}
        )
        self.session.execute(stmt)


class SqlAlchemySink(DynamicSink):
    def __init__(self, model_cls: type[Base],
                 index_elements: list[str],
                 set_elements: list[str],
                 engine: Engine):
        self.model_cls = model_cls
        self.index_elements = index_elements
        self.set_elements = set_elements
        self.engine = engine

    def build(self, step_id: str, worker_index: int, worker_count: int):
        with Session(self.engine) as session:
            return SqlAlchemyPartition(model_cls=self.model_cls,
                                       index_elements=self.index_elements,
                                       set_elements=self.set_elements,
                                       session=session)
