from __future__ import annotations

from typing import Any, Protocol

from .models import DescribeTypeResult


class TypeDescriberProtocol(Protocol):
    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None: ...


class StrictTypeDescriberProtocol(TypeDescriberProtocol, Protocol):
    def __call__(self, *, dtype: Any) -> DescribeTypeResult: ...


__all__ = ["StrictTypeDescriberProtocol", "TypeDescriberProtocol"]
