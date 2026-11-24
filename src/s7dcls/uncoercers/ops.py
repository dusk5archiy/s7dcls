from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .models import UncoerceResult
from .protocol import UncoercerProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchUncoercer(UncoercerProtocol):
    uncoercers: Sequence[UncoercerProtocol]

    def __call__(self, *, value: Any) -> UncoerceResult | None:
        for uncoercer in self.uncoercers:
            result = uncoercer(value=value)
            if result is not None:
                return result
        return None


__all__ = ["FirstMatchUncoercer"]
