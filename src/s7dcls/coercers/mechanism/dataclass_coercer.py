from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import JsonCoercerWorkerProtocol
from s7dcls.dataclass_hydrators.protocol import DataclassHydratorProtocol
from s7dcls.type_hints import resolve_dataclass_type


@dataclass(kw_only=True, frozen=True)
class DataclassCoercerWorker(JsonCoercerWorkerProtocol):
    dataclass_hydrator: DataclassHydratorProtocol

    def can_handle(self, *, dtype: Any) -> bool:
        return resolve_dataclass_type(dtype) is not None

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Any] | None:
        if resolve_dataclass_type(dtype) is None:
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


__all__ = ["DataclassCoercerWorker"]
