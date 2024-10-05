import asyncio
import pathlib
import statistics
from datetime import timedelta, timezone, datetime
from typing import Tuple

import bytewax.operators as op
from bytewax.connectors.files import DirSource
from bytewax.dataflow import Dataflow
from bytewax.inputs import Source
from bytewax.operators import windowing as window_op
from bytewax.operators.windowing import TumblingWindower, EventClock, WindowMetadata
from bytewax.outputs import Sink

from common import db
from common.settings import get_settings
from ingest import utils
from ingest.models import LogRecord
from ingest.sinks.sql_alchemy_sink import SqlAlchemySink
from models import ResourceStatisticsByDay

align_to = datetime(2024, 1, 1, tzinfo=timezone.utc)


def calc_avg(window_out: Tuple[str, Tuple[
    Tuple[int, list[LogRecord]],
    Tuple[int, WindowMetadata]
]]) -> dict:
    (customer_id, ((_, records), (_, window_meta))) = window_out
    return {
        "customer_id": customer_id,
        "date": records[0].date,
        "success_requests": sum(1 for r in records if r.is_success),
        "failed_requests": sum(1 for r in records if not r.is_success),
        "duration_mean": statistics.fmean(r.duration for r in records),
        "duration_p50": utils.percentile_sorted(sorted(r.duration for r in records), 50),
        "duration_p99": utils.percentile_sorted(sorted(r.duration for r in records), 99),
    }


def get_log_parser_flow(source: Source, sink: Sink,
                        window_length: timedelta = timedelta(days=1)) -> Dataflow:
    log_parser_flow = Dataflow("log_parser")
    logs_stream = op.input(step_id="inp", flow=log_parser_flow, source=source)
    parsed_logs = op.map(step_id="parse", up=logs_stream, mapper=LogRecord.from_string)
    filtered_logs = op.filter(step_id="filter", up=parsed_logs, predicate=lambda e: e is not None)
    keyed_stream = op.key_on(step_id="key_on_customer_id", up=filtered_logs, key=lambda e: e.customer_id)
    clock = EventClock(ts_getter=lambda e: e.date, wait_for_system_duration=timedelta.max)
    windower = TumblingWindower(length=window_length, align_to=align_to)
    win_out = window_op.collect_window(step_id="add", up=keyed_stream, clock=clock, windower=windower)
    merged_stream = op.join("join", win_out.down, win_out.meta, insert_mode="product")
    stats = op.map("stats", merged_stream, calc_avg)
    op.output("out", stats, sink)
    return log_parser_flow


settings = get_settings()

flow = get_log_parser_flow(
    source=DirSource(pathlib.Path(settings.LOGS_SOURCE_DIR), glob_pat="*.log"),
    sink=SqlAlchemySink(engine=db.get_engine(),
                        model_cls=ResourceStatisticsByDay,
                        index_elements=["customer_id", "date"],
                        set_elements=['success_requests', 'failed_requests',
                                      'duration_mean', 'duration_p50', 'duration_p99']))
