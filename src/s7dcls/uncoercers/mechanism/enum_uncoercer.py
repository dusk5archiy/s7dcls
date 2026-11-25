from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerProtocol, UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class EnumUncoercerWorker(UncoercerWorkerProtocol):
    hub: UncoercerProtocol

    def __call__(self, *, value):
        if isinstance(value, Enum):
            return UncoerceResult(value=self.hub(value=value.value))
        return None


__all__ = ["EnumUncoercerWorker"]
