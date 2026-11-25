from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, JsonCoercerWorkerProtocol
from s7dcls.error_paths import ErrorBatch


@dataclass(kw_only=True, frozen=True)
class SetCoercerWorker(JsonCoercerWorkerProtocol):
    hub: CoercerProtocol
    collect_errors: bool = False

    def can_handle(self, *, dtype: Any) -> bool:
        return dtype in (set, frozenset) or get_origin(dtype) in (set, frozenset)

    def __call__(
        self, *, value: Any, dtype: Any
    ) -> CoerceResult[set[Any] | frozenset[Any]] | None:
        origin = get_origin(dtype)
        target: Any = origin if origin in (set, frozenset) else dtype
        if target not in (set, frozenset):
            return None

        if not isinstance(value, list):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(list),
                    "got_type": str(type(value)),
                }
            )

        if origin is None:
            return CoerceResult(value=target(value))

        elem_type = get_args(dtype)[0]
        _results: list[Any] = []
        batch = ErrorBatch(collect=self.collect_errors)
        for idx, item in enumerate(value):
            with batch.capture(segment=idx):
                _results.append(self.hub(value=item, dtype=elem_type))
        batch.raise_if_any()
        return CoerceResult(value=target(_results))


__all__ = ["SetCoercerWorker"]
