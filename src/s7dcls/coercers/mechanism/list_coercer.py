from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, JsonCoercerWorkerProtocol
from s7dcls.error_paths import ErrorBatch


@dataclass(kw_only=True, frozen=True)
class ListCoercerWorker(JsonCoercerWorkerProtocol):
    hub: CoercerProtocol
    collect_errors: bool = False

    def can_handle(self, *, dtype: Any) -> bool:
        return dtype is list or get_origin(dtype) is list

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[list[Any]] | None:
        if dtype is not list and get_origin(dtype) is not list:
            return None

        if not isinstance(value, list):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(list),
                    "got_type": str(type(value)),
                }
            )

        if get_origin(dtype) is None:
            return CoerceResult(value=list(value))

        elem_type = get_args(dtype)[0]
        _results: list[Any] = []
        batch = ErrorBatch(collect=self.collect_errors)
        for idx, item in enumerate(value):
            with batch.capture(segment=idx):
                _results.append(self.hub(value=item, dtype=elem_type))
        batch.raise_if_any()
        return CoerceResult(value=_results)


__all__ = ["ListCoercerWorker"]
