from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .models import ValidateResult
from .protocol import ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchValidatorWorker(ValidatorWorkerProtocol):
    workers: Sequence[ValidatorWorkerProtocol]

    def __call__(self, *, value: Any, dtype: Any) -> ValidateResult | None:
        for worker in self.workers:
            result = worker(value=value, dtype=dtype)
            if result is not None:
                return result
        return None


__all__ = ["FirstMatchValidatorWorker"]
