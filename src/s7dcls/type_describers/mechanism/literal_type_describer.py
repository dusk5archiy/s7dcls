from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, get_args, get_origin

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class LiteralTypeDescriberWorker(TypeDescriberWorkerProtocol):
    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) is not Literal:
            return None
        return DescribeTypeResult(
            schema={"type": "literal", "choices": list(get_args(dtype))}
        )


__all__ = ["LiteralTypeDescriberWorker"]
