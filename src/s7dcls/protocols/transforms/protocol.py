from __future__ import annotations

from typing import Protocol


class TransformProtocol[T](Protocol):
    def __call__(self, x: T, /) -> T: ...


__all__ = ["TransformProtocol"]
