from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class UuidUncoercerWorker(UncoercerWorkerProtocol):
    def __call__(self, *, value):
        if isinstance(value, UUID):
            return UncoerceResult(value=str(value))
        return None


__all__ = ["UuidUncoercerWorker"]
