from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class NoneTypeDescriber(TypeDescriberProtocol):
    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if dtype is type(None):
            return DescribeTypeResult(schema={"type": "null"})
        return None


__all__ = ["NoneTypeDescriber"]
