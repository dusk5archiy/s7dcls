from __future__ import annotations

from typing import Any, Protocol

from .models import CoerceResult


class CoercerProtocol(Protocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult | None: ...


class StrictCoercerProtocol(CoercerProtocol, Protocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult: ...


class JsonCoercerProtocol(CoercerProtocol, Protocol):
    def can_handle(self, *, dtype: Any) -> bool: ...


class StrictJsonCoercerProtocol(
    StrictCoercerProtocol, JsonCoercerProtocol, Protocol
): ...


__all__ = [
    "CoercerProtocol",
    "JsonCoercerProtocol",
    "StrictCoercerProtocol",
    "StrictJsonCoercerProtocol",
]
