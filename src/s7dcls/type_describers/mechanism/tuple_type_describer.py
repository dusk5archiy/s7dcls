from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class TupleTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) is not tuple:
            return None

        args = get_args(dtype)
        if len(args) == 2 and args[1] is Ellipsis:
            return DescribeTypeResult(
                schema={
                    "type": "array",
                    "items": self.hub(dtype=args[0]),
                }
            )
        if args:
            return DescribeTypeResult(
                schema={
                    "type": "tuple",
                    "items": [self.hub(dtype=arg) for arg in args],
                }
            )
        return DescribeTypeResult(schema={"type": "array", "items": {"type": "any"}})


__all__ = ["TupleTypeDescriberWorker"]
