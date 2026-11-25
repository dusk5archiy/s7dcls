from __future__ import annotations

from dataclasses import dataclass

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class PrimitiveUncoercerWorker(UncoercerWorkerProtocol):
    def __call__(self, *, value):
        if isinstance(value, (bool, int, float, str)):
            return UncoerceResult(value=value)
        return None


__all__ = ["PrimitiveUncoercerWorker"]
