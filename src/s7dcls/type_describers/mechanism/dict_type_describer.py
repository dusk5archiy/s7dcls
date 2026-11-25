from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class DictTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) is not dict:
            return None

        args = get_args(dtype)
        key_schema = self.hub(dtype=args[0]) if len(args) >= 1 else {"type": "str"}
        value_schema = self.hub(dtype=args[1]) if len(args) >= 2 else {"type": "any"}
        return DescribeTypeResult(
            schema={"type": "dict", "key": key_schema, "value": value_schema}
        )


__all__ = ["DictTypeDescriberWorker"]
