from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAliasType

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class TypeAliasTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol
    active: set[TypeAliasType] = field(default_factory=set)

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if not isinstance(dtype, TypeAliasType):
            return None

        if dtype in self.active:
            return DescribeTypeResult(
                schema={"type": "alias_ref", "name": dtype.__name__}
            )

        self.active.add(dtype)
        try:
            return DescribeTypeResult(schema=self.hub(dtype=dtype.__value__))
        finally:
            self.active.discard(dtype)


__all__ = ["TypeAliasTypeDescriberWorker"]
