from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import ValidateResult
from ..protocol import ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class AnyValidatorWorker(ValidatorWorkerProtocol):
    def __call__(self, *, value, dtype):
        if dtype is not Any:
            return None

        return ValidateResult()


__all__ = ["AnyValidatorWorker"]
