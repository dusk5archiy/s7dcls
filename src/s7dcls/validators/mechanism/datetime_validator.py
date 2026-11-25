from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from ..models import ValidateResult
from ..protocol import ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class DateTimeValidatorWorker(ValidatorWorkerProtocol):
    def __call__(self, *, value, dtype):
        if dtype is datetime:
            if isinstance(value, datetime):
                return ValidateResult()
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(datetime),
                    "got_type": str(type(value)),
                }
            )

        if dtype is date:
            if isinstance(value, date) and not isinstance(value, datetime):
                return ValidateResult()
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(date),
                    "got_type": str(type(value)),
                }
            )

        if dtype is timedelta:
            if isinstance(value, timedelta):
                return ValidateResult()
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(timedelta),
                    "got_type": str(type(value)),
                }
            )

        return None


__all__ = ["DateTimeValidatorWorker"]
