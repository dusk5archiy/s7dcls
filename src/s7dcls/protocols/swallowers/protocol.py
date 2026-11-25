from __future__ import annotations

from typing import Protocol


class SwallowerProtocol[T](Protocol):
    def __call__(self, x: T, /) -> None: ...


__all__ = ["SwallowerProtocol"]
