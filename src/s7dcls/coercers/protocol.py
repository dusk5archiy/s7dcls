from __future__ import annotations

from typing import Any, Protocol, overload

from .models import CoerceResult


class CoercerWorkerProtocol(Protocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Any] | None: ...


class CoercerProtocol(Protocol):
    @overload
    def __call__[T](self, *, value: Any, dtype: type[T]) -> T: ...

    @overload
    def __call__(self, *, value: Any, dtype: Any) -> Any: ...


class CoercerSpawnerProtocol(Protocol):
    def __call__(self, hub: CoercerProtocol, /) -> CoercerWorkerProtocol: ...


class JsonCoercerWorkerProtocol(CoercerWorkerProtocol, Protocol):
    def can_handle(self, *, dtype: Any) -> bool: ...


class JsonCoercerProtocol(CoercerProtocol, Protocol):
    def can_handle(self, *, dtype: Any) -> bool: ...


__all__ = [
    "CoercerProtocol",
    "CoercerSpawnerProtocol",
    "CoercerWorkerProtocol",
    "JsonCoercerProtocol",
    "JsonCoercerWorkerProtocol",
]
