from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .protocol import SwallowerProtocol


@dataclass(kw_only=True, frozen=True)
class AllSwallower[T](SwallowerProtocol[T]):
    swallowers: Sequence[SwallowerProtocol[T]] = ()

    def __call__(self, x: T, /) -> None:
        for swallower in self.swallowers:
            swallower(x)


@dataclass(kw_only=True, frozen=True)
class AnySwallower[T](SwallowerProtocol[T]):
    swallowers: Sequence[SwallowerProtocol[T]] = ()
    exceptions: tuple[type[Exception], ...] = (Exception,)

    def __call__(self, x: T, /) -> None:
        errors: list[Exception] = []
        for swallower in self.swallowers:
            try:
                swallower(x)
                return
            except self.exceptions as exc:
                errors.append(exc)

        if errors:
            raise RuntimeError({"value": x, "errors": errors}) from errors[-1]
        raise ValueError({"value": x, "swallowers": ()})


__all__ = ["AllSwallower", "AnySwallower"]
