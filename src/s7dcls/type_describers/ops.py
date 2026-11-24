from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .models import DescribeTypeResult
from .protocol import TypeDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchTypeDescriber(TypeDescriberProtocol):
    describers: Sequence[TypeDescriberProtocol]

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        for describer in self.describers:
            result = describer(dtype=dtype)
            if result is not None:
                return result
        return None


__all__ = ["FirstMatchTypeDescriber"]
