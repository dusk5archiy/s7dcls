from __future__ import annotations

from dataclasses import dataclass

from ..models import ValidateResult
from ..protocol import ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class NoneValidatorWorker(ValidatorWorkerProtocol):
    def __call__(self, *, value, dtype):
        if dtype is not type(None) and dtype is not None:
            return None

        if value is None:
            return ValidateResult()

        raise TypeError(
            {
                "value": value,
                "expected_type": str(type(None)),
                "got_type": str(type(value)),
            }
        )


__all__ = ["NoneValidatorWorker"]
