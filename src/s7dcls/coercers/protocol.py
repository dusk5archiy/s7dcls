from __future__ import annotations

from typing import Any, Protocol, overload

from .models import CoerceResult


class CoercerProtocol(Protocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Any] | None: ...


class StrictCoercerProtocol(Protocol):
    @overload
    def __call__[T](self, *, value: Any, dtype: type[T]) -> T: ...

    @overload
    def __call__(self, *, value: Any, dtype: Any) -> Any: ...


class CoercerRecursionProtocol(Protocol):
    def __call__(self, inner_coercer: StrictCoercerProtocol, /) -> CoercerProtocol: ...


class JsonCoercerProtocol(CoercerProtocol, Protocol):
    def can_handle(self, *, dtype: Any) -> bool: ...


class StrictJsonCoercerProtocol(StrictCoercerProtocol, Protocol):
    def can_handle(self, *, dtype: Any) -> bool: ...


__all__ = [
    "CoercerProtocol",
    "CoercerRecursionProtocol",
    "JsonCoercerProtocol",
    "StrictCoercerProtocol",
    "StrictJsonCoercerProtocol",
]
