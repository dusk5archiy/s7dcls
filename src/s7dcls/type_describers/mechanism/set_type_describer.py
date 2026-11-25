from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class SetTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        origin = get_origin(dtype)
        if dtype not in (set, frozenset) and origin not in (set, frozenset):
            return None

        args = get_args(dtype)
        items = self.hub(dtype=args[0]) if args else {"type": "any"}
        return DescribeTypeResult(
            schema={"type": "array", "items": items, "unique": True}
        )


__all__ = ["SetTypeDescriberWorker"]
