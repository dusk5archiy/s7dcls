from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, is_dataclass
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import JsonCoercerProtocol
from s7dcls.dataclass_hydrators.protocol import DataclassHydratorProtocol


@dataclass(kw_only=True, frozen=True)
class DataclassCoercer(JsonCoercerProtocol):
    dataclass_hydrator: DataclassHydratorProtocol

    def can_handle(self, *, dtype: Any) -> bool:
        return isinstance(dtype, type) and is_dataclass(dtype)

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Any] | None:
        if not isinstance(dtype, type) or not is_dataclass(dtype):
            return None

        if not isinstance(value, Mapping):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(Mapping),
                    "got_type": str(type(value)),
                }
            )

        return CoerceResult(
            value=self.dataclass_hydrator(
                data=value,
                datacls=dtype,
            )
        )


__all__ = ["DataclassCoercer"]
