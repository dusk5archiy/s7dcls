from __future__ import annotations

from typing import Any, Protocol

from .models import UncoerceResult


class UncoercerWorkerProtocol(Protocol):
    def __call__(self, *, value: Any) -> UncoerceResult | None: ...


class UncoercerProtocol(Protocol):
    def __call__(self, *, value: Any) -> Any: ...


class UncoercerSpawnerProtocol(Protocol):
    def __call__(self, hub: UncoercerProtocol, /) -> UncoercerWorkerProtocol: ...


__all__ = [
    "UncoercerProtocol",
    "UncoercerSpawnerProtocol",
    "UncoercerWorkerProtocol",
]
