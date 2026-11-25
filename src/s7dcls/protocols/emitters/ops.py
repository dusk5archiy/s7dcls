from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..swallowers.protocol import SwallowerProtocol
from ..transforms.protocol import TransformProtocol
from .protocol import EmitterProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchEmitter[T](EmitterProtocol[T | None]):
    emitters: Sequence[EmitterProtocol[T | None]] = ()

    def __call__(self) -> T | None:
        for emitter in self.emitters:
            result = emitter()
            if result is not None:
                return result
        return None


@dataclass(kw_only=True, frozen=True)
class DefaultEmitter[T](EmitterProtocol[T]):
    emitter: EmitterProtocol[T | None]
    default: EmitterProtocol[T]

    def __call__(self) -> T:
        result = self.emitter()
        if result is not None:
            return result
        return self.default()


@dataclass(kw_only=True, frozen=True)
class FallbackEmitter[T](EmitterProtocol[T]):
    emitters: Sequence[EmitterProtocol[T]] = ()
    exceptions: tuple[type[Exception], ...] = (Exception,)

    def __call__(self) -> T:
        errors: list[Exception] = []
        for emitter in self.emitters:
            try:
                return emitter()
            except self.exceptions as exc:
                errors.append(exc)

        if errors:
            raise RuntimeError({"errors": errors}) from errors[-1]
        raise ValueError({"emitters": ()})


@dataclass(kw_only=True, frozen=True)
class DecoratedEmitter[T](EmitterProtocol[T]):
    emitter: EmitterProtocol[T]
    transform: TransformProtocol[T]

    def __call__(self) -> T:
        return self.transform(self.emitter())


@dataclass(kw_only=True, frozen=True)
class TappedEmitter[T](EmitterProtocol[T]):
    emitter: EmitterProtocol[T]
    swallower: SwallowerProtocol[T]

    def __call__(self) -> T:
        result = self.emitter()
        self.swallower(result)
        return result


__all__ = [
    "DecoratedEmitter",
    "DefaultEmitter",
    "FallbackEmitter",
    "FirstMatchEmitter",
    "TappedEmitter",
]
