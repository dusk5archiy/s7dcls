from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .protocol import StringTransformProtocol


@dataclass(kw_only=True, frozen=True)
class SequenceTransform(StringTransformProtocol):
    transforms: Sequence[StringTransformProtocol] = ()

    def __call__(self, string: str) -> str:
        for transform in self.transforms:
            string = transform(string)

        return string


__all__ = ["SequenceTransform"]
