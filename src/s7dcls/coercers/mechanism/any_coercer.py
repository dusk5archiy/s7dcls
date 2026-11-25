from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class AnyCoercerWorker(CoercerWorkerProtocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Any] | None:
        if dtype is not Any:
            return None

        return CoerceResult(value=value)


__all__ = ["AnyCoercerWorker"]
