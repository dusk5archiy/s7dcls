from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class NoneTypeDescriberWorker(TypeDescriberWorkerProtocol):
    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if dtype is type(None):
            return DescribeTypeResult(schema={"type": "null"})
        return None


__all__ = ["NoneTypeDescriberWorker"]
