import collections
import dataclasses
import itertools
import math
import statistics
from collections import namedtuple
from datetime import timedelta, timezone, datetime
from http import HTTPStatus
from pathlib import Path
from typing import Tuple, TypeAlias, Any

from bytewax._bytewax import run_main
from bytewax.connectors.files import DirSource
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
import bytewax.operators as op
from bytewax.operators.windowing import TumblingWindower, EventClock
from bytewax.testing import TestingSink


@dataclasses.dataclass
class LogRecord:
    date: datetime.date
    customer_id: str
    success_durations: list[float]
    failed_durations: list[float]

    @classmethod
    def from_string(cls, s, delimiter=' '):
        parts = s.split(delimiter)
        is_success = HTTPStatus(int(parts[4])).is_success
        date = datetime.strptime(parts[0], "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
        customer_id = parts[2]
        duration = float(parts[5])
        return LogRecord(
            date=date,
            customer_id=customer_id,
            success_durations=[duration] if is_success else [],
            failed_durations=[duration] if not is_success else [],
        )


def percentile_sorted(data, perc: int):
    size = len(data)
    return data[int(math.ceil((size * perc) / 100)) - 1]


def test_dir_input():
    out = []

    flow = Dataflow("test_df")

    dir_source = DirSource(
        dir_path=Path("/Users/ainur.timerbaev/code/rated-assesment/logs"),
        glob_pat="*.log")
    logs_stream = op.input(step_id="inp", flow=flow, source=dir_source)

    parsed_logs = op.map(step_id="parse", up=logs_stream, mapper=LogRecord.from_string)
    keyed_stream = op.key_on("key_on_customer_id_and_date", parsed_logs, lambda e: f"{e.customer_id}/{e.date}")

    def reducer(x: LogRecord, y: LogRecord) -> LogRecord:
        return LogRecord(
            date=x.date,
            customer_id=x.customer_id,
            success_durations=x.success_durations + y.success_durations,
            failed_durations=x.failed_durations + y.failed_durations
        )

    def mapper(key_state: Tuple[str, LogRecord]) -> dict:
        key, final_log = key_state
        return {
            "customer_id": final_log.customer_id,
            "date": final_log.date,
            "success_requests": len(final_log.success_durations),
            "failed_requests": len(final_log.failed_durations),
        }
    stats = op.reduce_final("reduce", keyed_stream, reducer).then(op.map, "fmt", mapper)

    op.output("out", stats, TestingSink(out))

    run_main(flow)
    cust_10_data = [e for e in out if e["customer_id"] == "cust_10"]
    total_requests = sum(e["success_requests"] + e["failed_requests"] for e in cust_10_data)
    assert total_requests == 185

