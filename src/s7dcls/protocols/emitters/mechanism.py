from __future__ import annotations

from dataclasses import dataclass

from .protocol import EmitterProtocol


@dataclass(kw_only=True, frozen=True)
class ConstEmitter[T](EmitterProtocol[T]):
    value: T

    def __call__(self) -> T:
        return self.value


__all__ = ["ConstEmitter"]
