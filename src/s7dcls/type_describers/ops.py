from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .models import DescribeTypeResult
from .protocol import TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchTypeDescriberWorker(TypeDescriberWorkerProtocol):
    workers: Sequence[TypeDescriberWorkerProtocol]

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        for worker in self.workers:
            result = worker(dtype=dtype)
            if result is not None:
                return result
        return None


__all__ = ["FirstMatchTypeDescriberWorker"]
