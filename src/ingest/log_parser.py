import asyncio
import pathlib
import statistics
from collections import namedtuple
from dataclasses import dataclass
from datetime import timedelta, timezone, datetime
from typing import Tuple

import bytewax.operators as op
from bytewax.connectors.files import DirSource
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.inputs import Source
from bytewax.operators import windowing as window_op
from bytewax.operators.windowing import TumblingWindower, EventClock, WindowMetadata
from bytewax.outputs import Sink

from src.ingest import utils
from src.ingest.models import LogRecord
from src.ingest.sinks.sql_model_sink import SqlModelSink
from src.models import ResourceStatisticsByDay

align_to = datetime(2024, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True)
class Stats:
    success_durations: list[float]
    failed_durations: list[float]


KEY_DELIMITER = "/"


def calc_avg(window_out: Tuple[str, Stats]) -> dict:
    key, stats = window_out
    customer_id, date = key.split(KEY_DELIMITER)
    all_durations = sorted(stats.success_durations + stats.failed_durations)
    return {
        "customer_id": customer_id,
        "date": date,
        "success_requests": len(stats.success_durations),
        "failed_requests": len(stats.failed_durations),
        "duration_mean": statistics.fmean(all_durations),
        "duration_p50": utils.percentile_sorted(all_durations, 50),
        "duration_p99": utils.percentile_sorted(all_durations, 99),
    }


def get_log_parser_flow(source: Source, sink: Sink) -> Dataflow:
    log_parser_flow = Dataflow("log_parser")
    logs_stream = op.input(step_id="inp", flow=log_parser_flow, source=source)
    parsed_logs = op.map(step_id="parse", up=logs_stream, mapper=LogRecord.from_string)
    filtered_logs = op.filter(step_id="filter", up=parsed_logs, predicate=lambda e: e is not None)
    keyed_stream = op.key_on(step_id="key_on_customer_id_and_date", up=filtered_logs,
                             key=lambda e: KEY_DELIMITER.join([e.customer_id, e.date]))

    def key_init(record_tuple: Tuple[str, LogRecord]) -> Tuple[str, Stats]:
        key, record = record_tuple
        return key, Stats(
            success_durations=[record.duration] if record.is_success else [],
            failed_durations=[record.duration] if not record.is_success else []
        )

    def reducer(x: Stats, y: Stats) -> Stats:
        return Stats(
            success_durations=x.success_durations + y.success_durations,
            failed_durations=x.failed_durations + y.failed_durations
        )

    mapped_to_state = op.map("map_to_state", keyed_stream, key_init)
    reduced = op.reduce_final("reduce", mapped_to_state, reducer)
    stats = op.map("stats", reduced, calc_avg)
    op.output("out", stats, sink)
    return log_parser_flow


dir_source = DirSource(pathlib.Path("/Users/ainur.timerbaev/code/rated-assesment/logs"), glob_pat="*.log")
stdout_sink = StdOutSink()
sql_model_sink = SqlModelSink(model_cls=ResourceStatisticsByDay)
flow = get_log_parser_flow(source=dir_source, sink=sql_model_sink)
