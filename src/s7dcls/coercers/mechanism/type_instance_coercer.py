from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol


@dataclass(kw_only=True, frozen=True)
class TypeInstanceCoercer[T](CoercerProtocol):
    datatype: type[T]

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[T] | None:
        if dtype is not self.datatype:
            return None

        if self.datatype is int:
            if isinstance(value, int) and not isinstance(value, bool):
                return CoerceResult(value=cast(T, value))
        elif self.datatype is float:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return CoerceResult(value=cast(T, float(value)))
        elif isinstance(value, self.datatype):
            return CoerceResult(value=value)

        raise TypeError(
            {
                "value": value,
                "expected_type": str(self.datatype),
                "got_type": str(type(value)),
            }
        )


__all__ = ["TypeInstanceCoercer"]
