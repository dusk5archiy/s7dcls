from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..models import ValidateResult
from ..protocol import ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class EnumValidatorWorker(ValidatorWorkerProtocol):
    def __call__(self, *, value, dtype):
        if not isinstance(dtype, type) or not issubclass(dtype, Enum):
            return None

        if isinstance(value, dtype):
            return ValidateResult()

        raise TypeError(
            {
                "value": value,
                "expected_type": str(dtype),
                "got_type": str(type(value)),
            }
        )


__all__ = ["EnumValidatorWorker"]
