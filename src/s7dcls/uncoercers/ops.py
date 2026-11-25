from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .models import UncoerceResult
from .protocol import UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchUncoercerWorker(UncoercerWorkerProtocol):
    workers: Sequence[UncoercerWorkerProtocol]

    def __call__(self, *, value: Any) -> UncoerceResult | None:
        for worker in self.workers:
            result = worker(value=value)
            if result is not None:
                return result
        return None


__all__ = ["FirstMatchUncoercerWorker"]
