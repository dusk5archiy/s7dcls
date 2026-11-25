from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .protocol import TransformProtocol


@dataclass(kw_only=True, frozen=True)
class SequenceTransform[T](TransformProtocol[T]):
    transforms: Sequence[TransformProtocol[T]] = ()

    def __call__(self, x: T, /) -> T:
        current = x
        for transform in self.transforms:
            current = transform(current)
        return current


__all__ = ["SequenceTransform"]
