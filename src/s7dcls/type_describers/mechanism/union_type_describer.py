from __future__ import annotations

from dataclasses import dataclass
from types import UnionType
from typing import Any, Union, get_args, get_origin

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class UnionTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) not in (UnionType, Union):
            return None

        raw_args = get_args(dtype)
        non_none = [arg for arg in raw_args if arg is not type(None)]
        nullable = len(non_none) < len(raw_args)

        schema: dict[str, Any]
        if len(non_none) == 1:
            schema = dict(self.hub(dtype=non_none[0]))
        else:
            schema = {
                "type": "union",
                "variants": [self.hub(dtype=arg) for arg in non_none],
            }

        schema["nullable"] = nullable
        return DescribeTypeResult(schema=schema)


__all__ = ["UnionTypeDescriberWorker"]
