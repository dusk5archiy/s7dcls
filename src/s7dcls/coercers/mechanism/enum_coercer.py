from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, CoercerWorkerProtocol


def _matches_enum_value(value: Any, member_value: Any) -> bool:
    if isinstance(value, bool) != isinstance(member_value, bool):
        return False
    return bool(member_value == value)


@dataclass(kw_only=True, frozen=True)
class EnumCoercerWorker(CoercerWorkerProtocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Enum] | None:
        if not isinstance(dtype, type) or not issubclass(dtype, Enum):
            return None

        if isinstance(value, dtype):
            return CoerceResult(value=value)

        for member in dtype:
            if _matches_enum_value(value, member.value):
                return CoerceResult(value=member)

        raise ValueError(
            {
                "value": value,
                "expected_type": str(dtype),
                "allowed": [member.value for member in dtype],
            }
        )


@dataclass(kw_only=True, frozen=True)
class StringEnumCoercerWorker(CoercerWorkerProtocol):
    hub: CoercerProtocol

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Enum] | None:
        if not isinstance(dtype, type) or not issubclass(dtype, Enum):
            return None

        if isinstance(value, dtype):
            return CoerceResult(value=value)

        if not isinstance(value, str):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(str),
                    "got_type": str(type(value)),
                }
            )

        for member in dtype:
            if isinstance(member.value, str):
                if member.value == value:
                    return CoerceResult(value=member)
                continue
            try:
                coerced = self.hub(value=value, dtype=type(member.value))
            except (TypeError, ValueError):
                continue
            if _matches_enum_value(coerced, member.value):
                return CoerceResult(value=member)

        raise ValueError(
            {
                "value": value,
                "expected_type": str(dtype),
                "allowed": [member.value for member in dtype],
            }
        )


__all__ = ["EnumCoercerWorker", "StringEnumCoercerWorker"]
