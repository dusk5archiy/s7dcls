from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class DateTimeUncoercerWorker(UncoercerWorkerProtocol):
    def __call__(self, *, value):
        if isinstance(value, (datetime, date)):
            return UncoerceResult(value=value.isoformat())
        if isinstance(value, timedelta):
            return UncoerceResult(value=value.total_seconds())
        return None


__all__ = ["DateTimeUncoercerWorker"]
