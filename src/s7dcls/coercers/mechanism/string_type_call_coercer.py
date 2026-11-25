from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class StringTypeCallCoercerWorker[T](CoercerWorkerProtocol):
    datatype: type[T]

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[T] | None:
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
            ctor = cast(Callable[[str], T], self.datatype)
            return CoerceResult(value=ctor(value))
        except (ValueError, TypeError) as e:
            raise type(e)(
                {"value": value, "expected_type": str(dtype), "error": e}
            ) from e


__all__ = ["StringTypeCallCoercerWorker"]
