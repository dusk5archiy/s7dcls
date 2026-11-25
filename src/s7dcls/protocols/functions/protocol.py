from __future__ import annotations

from typing import Protocol


class FunctionProtocol[X, Y](Protocol):
    def __call__(self, x: X, /) -> Y: ...


__all__ = ["FunctionProtocol"]
