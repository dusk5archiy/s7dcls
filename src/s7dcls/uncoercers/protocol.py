from __future__ import annotations

from typing import Any, Protocol

from .models import UncoerceResult


class UncoercerProtocol(Protocol):
    def __call__(self, *, value: Any) -> UncoerceResult | None: ...


class StrictUncoercerProtocol(Protocol):
    def __call__(self, *, value: Any) -> Any: ...


__all__ = ["StrictUncoercerProtocol", "UncoercerProtocol"]
