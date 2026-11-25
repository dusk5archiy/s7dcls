from __future__ import annotations

from dataclasses import dataclass

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerProtocol, UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class SequenceUncoercerWorker(UncoercerWorkerProtocol):
    hub: UncoercerProtocol

    def __call__(self, *, value):
        if not isinstance(value, (list, tuple)):
            return None
        return UncoerceResult(value=[self.hub(value=item) for item in value])


__all__ = ["SequenceUncoercerWorker"]
