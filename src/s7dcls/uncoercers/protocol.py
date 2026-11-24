from __future__ import annotations

from typing import Any, Protocol

from .models import UncoerceResult


class UncoercerProtocol(Protocol):
    def __call__(self, *, value: Any) -> UncoerceResult | None: ...


class StrictUncoercerProtocol(Protocol):
    def __call__(self, *, value: Any) -> Any: ...


class UncoercerRecursionProtocol(Protocol):
    def __call__(
        self, inner_uncoercer: StrictUncoercerProtocol, /
    ) -> UncoercerProtocol: ...


__all__ = [
    "StrictUncoercerProtocol",
    "UncoercerProtocol",
    "UncoercerRecursionProtocol",
]
