import statistics
from datetime import timedelta, timezone, datetime
from typing import Tuple

import bytewax.operators as op
from bytewax.connectors.files import DirSource
from bytewax.dataflow import Dataflow
from bytewax.inputs import Source
from bytewax.operators import windowing as window_op
from bytewax.operators.windowing import TumblingWindower, EventClock
from bytewax.outputs import Sink

from common import db
from common.settings import get_settings
from ingest import utils
from ingest.models import LogRecord
from ingest.sinks.sql_alchemy_sink import SqlAlchemySink
from models import ResourceStatisticsByDay

align_to = datetime(2024, 1, 1, tzinfo=timezone.utc)


def calc_statistics(window_out: Tuple[str, Tuple[int, list[LogRecord]]]) -> dict:
    customer_id, (_, records) = window_out
    sorted_durations = sorted(r.duration for r in records)
    uptime_duration = tuple(r.duration for r in records if r.is_success)
    downtime_duration = tuple(r.duration for r in records if not r.is_success)
    uptime = sum(uptime_duration)
    downtime = sum(downtime_duration)
    total_time = uptime + downtime
    uptime_percentage = (uptime / total_time) * 100 if total_time > 0 else 0.0
    return {
        "customer_id": customer_id,
        "date": records[0].date,
        "success_requests": len(uptime_duration),
        "failed_requests": len(downtime_duration),
        "duration_mean": statistics.fmean(sorted_durations),
        "duration_p50": utils.percentile_sorted(sorted_durations, 50),
        "duration_p99": utils.percentile_sorted(sorted_durations, 99),
        "uptime_percentage": uptime_percentage
    }


def get_log_parser_flow(source: Source, sink: Sink,
                        window_length: timedelta = timedelta(days=1),
                        wait_for_system_duration=timedelta.max) -> Dataflow:
    log_parser_flow = Dataflow("log_parser")
    logs_stream = op.input(step_id="inp", flow=log_parser_flow, source=source)
    parsed_logs = op.map(step_id="parse", up=logs_stream, mapper=LogRecord.from_string)
    filtered_logs = op.filter(step_id="filter", up=parsed_logs, predicate=lambda e: e is not None)
    keyed_stream = op.key_on(step_id="key_on_customer_id", up=filtered_logs, key=lambda e: e.customer_id)
    clock = EventClock(ts_getter=lambda e: e.date, wait_for_system_duration=wait_for_system_duration)
    windower = TumblingWindower(length=window_length, align_to=align_to)
    win_out = window_op.collect_window(step_id="add", up=keyed_stream, clock=clock, windower=windower)
    stats = op.map("stats", win_out.down, calc_statistics)
    op.output("out", stats, sink)
    return log_parser_flow


settings = get_settings()

flow = get_log_parser_flow(
    source=DirSource(settings.LOGS_SOURCE_DIR, glob_pat="*.log"),
    sink=SqlAlchemySink(engine=db.get_engine(),
                        model_cls=ResourceStatisticsByDay,
                        index_elements=["customer_id", "date"],
                        set_elements=['success_requests', 'failed_requests',
                                      'duration_mean', 'duration_p50', 'duration_p99',
                                      'uptime_percentage']),
    wait_for_system_duration=settings.WAIT_FOR_SYSTEM_DURATION)
