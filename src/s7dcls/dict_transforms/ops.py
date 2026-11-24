from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .protocol import DictTransformProtocol


@dataclass(kw_only=True, frozen=True)
class SequenceDictTransform(DictTransformProtocol):
    transforms: Sequence[DictTransformProtocol] = ()

    def __call__(self, x: Mapping[str, Any]) -> dict[str, Any]:
        current: Mapping[str, Any] = x
        for transform in self.transforms:
            current = transform(current)
        return dict(current)


__all__ = ["SequenceDictTransform"]
