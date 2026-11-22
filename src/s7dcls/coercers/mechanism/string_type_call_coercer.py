from __future__ import annotations

from dataclasses import dataclass

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol


@dataclass(kw_only=True, frozen=True)
class StringTypeCallCoercer(CoercerProtocol):
    datatype: type

    def __call__(self, *, value, dtype):
        if dtype is not self.datatype:
            return None

        if not isinstance(value, str):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(str),
                    "got_type": str(type(value)),
                }
            )

        try:
            return CoerceResult(value=self.datatype(value))
        except (ValueError, TypeError) as e:
            raise type(e)({"value": value, "expected_type": str(dtype), "e": e}) from e


__all__ = ["StringTypeCallCoercer"]
