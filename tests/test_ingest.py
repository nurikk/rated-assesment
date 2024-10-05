import asyncio
import datetime
import pathlib

from bytewax._bytewax import run_main
from bytewax.connectors.files import DirSource
from bytewax.testing import TestingSink

from ingest.log_parser import get_log_parser_flow
from ingest.sinks.sql_model_sink import SqlModelSink
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


def test_ingest_file():
    out = []
    test_sink = TestingSink(out)
    test_source = DirSource(pathlib.Path("/Users/ainur.timerbaev/code/rated-assesment/logs"), glob_pat="*.log")
    flow = get_log_parser_flow(source=test_source, sink=test_sink)
    run_main(flow)
    cust_1_data = [e for e in out if e["customer_id"] == "cust_1"]
    success_requests = sum(e["success_requests"] for e in cust_1_data)
    failed_requests = sum(e["failed_requests"] for e in cust_1_data)
    assert success_requests == 73
    assert failed_requests == 155


def test_sqlmodel_sink(test_source, in_memory_db):
    test_sink = SqlModelSink(model_cls=ResourceStatisticsByDay)

    flow = get_log_parser_flow(source=test_source, sink=test_sink)
    run_main(flow)

    async def get():
        return await ResourceStatisticsByDay.all().count()

    assert asyncio.run(get()) == 5
