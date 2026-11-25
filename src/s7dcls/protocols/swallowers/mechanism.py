from __future__ import annotations

from dataclasses import dataclass

from .protocol import SwallowerProtocol


@dataclass(kw_only=True, frozen=True)
class NoopSwallower[T](SwallowerProtocol[T]):
    def __call__(self, x: T, /) -> None:
        return None


__all__ = ["NoopSwallower"]
