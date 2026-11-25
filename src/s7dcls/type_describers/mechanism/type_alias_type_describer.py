from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, TypeAliasType

from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol

_ACTIVE_ALIASES: ContextVar[frozenset[TypeAliasType]] = ContextVar(
    "s7dcls_active_aliases", default=frozenset()
)


@dataclass(kw_only=True, frozen=True)
class TypeAliasTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if not isinstance(dtype, TypeAliasType):
            return None

        active = _ACTIVE_ALIASES.get()
        if dtype in active:
            return DescribeTypeResult(
                schema={"type": "alias_ref", "name": dtype.__name__}
            )

        token = _ACTIVE_ALIASES.set(active | {dtype})
        try:
            return DescribeTypeResult(schema=self.hub(dtype=dtype.__value__))
        finally:
            _ACTIVE_ALIASES.reset(token)


__all__ = ["TypeAliasTypeDescriberWorker"]
