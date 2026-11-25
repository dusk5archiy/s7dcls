from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class UuidCoercerWorker(CoercerWorkerProtocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[UUID] | None:
        if dtype is not UUID:
            return None

        if isinstance(value, UUID):
            return CoerceResult(value=value)

        if isinstance(value, str):
            try:
                return CoerceResult(value=UUID(value))
            except ValueError as e:
                raise ValueError(
                    {"value": value, "expected_type": str(UUID), "error": str(e)}
                ) from e

        raise TypeError(
            {
                "value": value,
                "expected_type": str(UUID),
                "got_type": str(type(value)),
            }
        )


__all__ = ["UuidCoercerWorker"]
