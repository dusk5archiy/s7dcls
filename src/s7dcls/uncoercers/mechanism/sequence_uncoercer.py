from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.error_paths import ErrorPath
from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerProtocol, UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class SequenceUncoercerWorker(UncoercerWorkerProtocol):
    hub: UncoercerProtocol

    def __call__(self, *, value):
        if not isinstance(value, (list, tuple)):
            return None
        items: list[Any] = []
        for idx, item in enumerate(value):
            with ErrorPath(segment=idx):
                items.append(self.hub(value=item))
        return UncoerceResult(value=items)


__all__ = ["SequenceUncoercerWorker"]
