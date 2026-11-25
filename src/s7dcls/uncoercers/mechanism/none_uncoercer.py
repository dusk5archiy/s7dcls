from __future__ import annotations

from dataclasses import dataclass

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class NoneUncoercerWorker(UncoercerWorkerProtocol):
    def __call__(self, *, value):
        if value is None:
            return UncoerceResult(value=None)
        return None


__all__ = ["NoneUncoercerWorker"]
