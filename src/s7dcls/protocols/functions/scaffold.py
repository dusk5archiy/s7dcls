from __future__ import annotations

from dataclasses import dataclass

from .protocol import FunctionProtocol


@dataclass(kw_only=True, frozen=True)
class ChainFunction[A, B, C](FunctionProtocol[A, C]):
    first: FunctionProtocol[A, B]
    second: FunctionProtocol[B, C]

    def __call__(self, x: A, /) -> C:
        return self.second(self.first(x))


__all__ = ["ChainFunction"]
