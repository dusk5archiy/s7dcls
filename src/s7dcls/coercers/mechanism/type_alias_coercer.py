from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAliasType

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, CoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class TypeAliasCoercerWorker(CoercerWorkerProtocol):
    hub: CoercerProtocol

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Any] | None:
        if isinstance(dtype, TypeAliasType):
            return CoerceResult(value=self.hub(value=value, dtype=dtype.__value__))
        return None


__all__ = ["TypeAliasCoercerWorker"]
