import asyncio
import datetime

import pytest
from bytewax._bytewax import run_main
from bytewax.testing import TestingSink
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ingest.log_parser import get_log_parser_flow
from ingest.models import LogRecord
from ingest.sinks.sql_alchemy_sink import SqlAlchemySink
from models import ResourceStatisticsByDay


def test_flow(test_source):
    out = []
    test_sink = TestingSink(out)

    flow = get_log_parser_flow(source=test_source, sink=test_sink)
    run_main(flow)
    cust_1_data = [e for e in out if e["customer_id"] == "cust_1"]
    success_requests = sum(e["success_requests"] for e in cust_1_data)
    failed_requests = sum(e["failed_requests"] for e in cust_1_data)
    assert success_requests == 2
    assert failed_requests == 3


def test_sqlmodel_sink(test_source, sync_engine):
    test_sink = SqlAlchemySink(engine=sync_engine,
                               model_cls=ResourceStatisticsByDay,
                               index_elements=["customer_id", "date"],
                               set_elements=['success_requests', 'failed_requests',
                                             'duration_mean', 'duration_p50', 'duration_p99'])

    flow = get_log_parser_flow(source=test_source, sink=test_sink)
    run_main(flow)

    with Session(sync_engine) as db_session:

        records_count = select(func.count()).select_from(ResourceStatisticsByDay)
        assert db_session.execute(records_count).scalar() == 5


@pytest.mark.parametrize('log, expected', [
    ('', None),
    (None, None),
    ('aa bb cc dd ee ff 11', None),
    ('assd-09-01 02:59:35 cust_1 /api/v1/resource4 aa 1.551', None),
    ('2024-09-01 02:59:35 cust_1 /api/v1/resource4 404 1.551', LogRecord(date=datetime.datetime(2024, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), customer_id='cust_1', is_success=False, duration=1.551)),

])
def test_log_parser(log, expected):
    assert LogRecord.from_string(log) == expected
