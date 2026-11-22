from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class TypeInstanceDescriber(TypeDescriberProtocol):
    datatype: type[Any]
    type_name: str

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if dtype is self.datatype:
            return DescribeTypeResult(schema={"type": self.type_name})
        return None


__all__ = ["TypeInstanceDescriber"]
