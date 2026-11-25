from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class ListTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if get_origin(dtype) is not list:
            return None

        args = get_args(dtype)
        items = self.hub(dtype=args[0]) if args else {"type": "any"}
        return DescribeTypeResult(schema={"type": "array", "items": items})


__all__ = ["ListTypeDescriberWorker"]
