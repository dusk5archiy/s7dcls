from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class EnumTypeDescriberWorker(TypeDescriberWorkerProtocol):
    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if not isinstance(dtype, type) or not issubclass(dtype, Enum):
            return None
        return DescribeTypeResult(
            schema={
                "type": "enum",
                "name": dtype.__name__,
                "choices": [member.value for member in dtype],
            }
        )


__all__ = ["EnumTypeDescriberWorker"]
