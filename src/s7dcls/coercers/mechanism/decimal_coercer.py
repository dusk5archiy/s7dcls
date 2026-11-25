from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class DecimalCoercerWorker(CoercerWorkerProtocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Decimal] | None:
        if dtype is not Decimal:
            return None

        if isinstance(value, Decimal):
            return CoerceResult(value=value)

        if isinstance(value, int) and not isinstance(value, bool):
            return CoerceResult(value=Decimal(value))

        if isinstance(value, str):
            try:
                return CoerceResult(value=Decimal(value))
            except InvalidOperation as e:
                raise ValueError(
                    {"value": value, "expected_type": str(Decimal), "error": str(e)}
                ) from e

        raise TypeError(
            {
                "value": value,
                "expected_type": str(Decimal),
                "got_type": str(type(value)),
            }
        )


__all__ = ["DecimalCoercerWorker"]
