from __future__ import annotations

from typing import Protocol


class EmitterProtocol[T](Protocol):
    def __call__(self) -> T: ...


__all__ = ["EmitterProtocol"]
