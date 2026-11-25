from __future__ import annotations

from dataclasses import dataclass

from .protocol import TransformProtocol


@dataclass(kw_only=True, frozen=True)
class IdentityTransform[T](TransformProtocol[T]):
    def __call__(self, x: T, /) -> T:
        return x


__all__ = ["IdentityTransform"]
