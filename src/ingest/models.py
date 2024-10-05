import datetime
from dataclasses import dataclass
from http import HTTPStatus


@dataclass(frozen=True)
class LogRecord:
    date: datetime.date
    customer_id: str
    is_success: bool
    duration: float

    @classmethod
    def from_string(cls, s, delimiter=' '):
        try:
            parts = s.split(delimiter)
            is_success = HTTPStatus(int(parts[4])).is_success
            return LogRecord(
                date=datetime.datetime.strptime(parts[0], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc),
                customer_id=parts[2],
                is_success=is_success,
                duration=float(parts[5])
            )
        except (ValueError, IndexError, AttributeError):
            return None
