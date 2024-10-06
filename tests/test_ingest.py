import asyncio
import datetime

import pytest
from bytewax._bytewax import run_main
from bytewax.testing import TestingSink
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ingest.log_parser import get_log_parser_flow, calc_statistics
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
    uptime_percentage = sum(e["uptime_percentage"] for e in cust_1_data)
    assert success_requests == 2
    assert failed_requests == 3
    assert uptime_percentage == 49.37238493723849


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


@pytest.mark.parametrize("window_out, expected", [
    (
        ("cust_1", (0, [
            LogRecord(date=datetime.datetime(2024, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), customer_id='cust_1', is_success=True, duration=1.0),
            LogRecord(date=datetime.datetime(2024, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), customer_id='cust_1', is_success=False, duration=2.0),
            LogRecord(date=datetime.datetime(2024, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), customer_id='cust_1', is_success=True, duration=3.0),
        ])),
        {
            "customer_id": "cust_1",
            "date": datetime.datetime(2024, 9, 1, 0, 0, tzinfo=datetime.timezone.utc),
            "success_requests": 2,
            "failed_requests": 1,
            "duration_mean": 2.0,
            "duration_p50": 2.0,
            "duration_p99": 3.0,
            "uptime_percentage": 66.66666666666666
        }
    ),
    (
        ("cust_2", (0, [
            LogRecord(date=datetime.datetime(2024, 9, 2, 0, 0, tzinfo=datetime.timezone.utc), customer_id='cust_2', is_success=False, duration=4.0),
            LogRecord(date=datetime.datetime(2024, 9, 2, 0, 0, tzinfo=datetime.timezone.utc), customer_id='cust_2', is_success=False, duration=5.0),
        ])),
        {
            "customer_id": "cust_2",
            "date": datetime.datetime(2024, 9, 2, 0, 0, tzinfo=datetime.timezone.utc),
            "success_requests": 0,
            "failed_requests": 2,
            "duration_mean": 4.5,
            "duration_p50": 4.0,
            "duration_p99": 5.0,
            "uptime_percentage": 0.0
        }
    ),
])
def test_calc_statistics(window_out, expected):
    assert calc_statistics(window_out) == expected
