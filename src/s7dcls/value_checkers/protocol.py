from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ValueCheckerProtocol(Protocol):
    def __call__(self, value: Any, /) -> None: ...


__all__ = ["ValueCheckerProtocol"]
