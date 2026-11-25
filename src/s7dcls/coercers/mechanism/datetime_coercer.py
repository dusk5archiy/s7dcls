from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class DateTimeCoercerWorker(CoercerWorkerProtocol):
    def __call__(
        self, *, value: Any, dtype: Any
    ) -> CoerceResult[datetime | date | timedelta] | None:
        if dtype is datetime:
            if isinstance(value, datetime):
                return CoerceResult(value=value)
            if isinstance(value, str):
                try:
                    return CoerceResult(value=datetime.fromisoformat(value))
                except ValueError as e:
                    raise ValueError(
                        {
                            "value": value,
                            "expected_type": str(datetime),
                            "error": str(e),
                        }
                    ) from e
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(datetime),
                    "got_type": str(type(value)),
                }
            )

        if dtype is date:
            if isinstance(value, date) and not isinstance(value, datetime):
                return CoerceResult(value=value)
            if isinstance(value, str):
                try:
                    return CoerceResult(value=date.fromisoformat(value))
                except ValueError as e:
                    raise ValueError(
                        {"value": value, "expected_type": str(date), "error": str(e)}
                    ) from e
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(date),
                    "got_type": str(type(value)),
                }
            )

        if dtype is timedelta:
            if isinstance(value, timedelta):
                return CoerceResult(value=value)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return CoerceResult(value=timedelta(seconds=value))
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(timedelta),
                    "got_type": str(type(value)),
                }
            )

        return None


@dataclass(kw_only=True, frozen=True)
class StringTimedeltaCoercerWorker(CoercerWorkerProtocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[timedelta] | None:
        if dtype is not timedelta:
            return None

        if isinstance(value, timedelta):
            return CoerceResult(value=value)

        if isinstance(value, str):
            try:
                return CoerceResult(value=timedelta(seconds=float(value)))
            except ValueError as e:
                raise ValueError(
                    {"value": value, "expected_type": str(timedelta), "error": str(e)}
                ) from e

        raise TypeError(
            {
                "value": value,
                "expected_type": str(str),
                "got_type": str(type(value)),
            }
        )


__all__ = ["DateTimeCoercerWorker", "StringTimedeltaCoercerWorker"]
