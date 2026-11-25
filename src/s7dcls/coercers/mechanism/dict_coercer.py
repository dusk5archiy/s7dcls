from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, JsonCoercerWorkerProtocol
from s7dcls.error_paths import ErrorBatch


@dataclass(kw_only=True, frozen=True)
class DictCoercerWorker(JsonCoercerWorkerProtocol):
    hub: CoercerProtocol
    collect_errors: bool = False

    def can_handle(self, *, dtype: Any) -> bool:
        return dtype is dict or get_origin(dtype) is dict

    def __call__(
        self, *, value: Any, dtype: Any
    ) -> CoerceResult[dict[Any, Any]] | None:
        if dtype is not dict and get_origin(dtype) is not dict:
            return None

        if not isinstance(value, dict):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(dict),
                    "got_type": str(type(value)),
                }
            )

        if get_origin(dtype) is None:
            return CoerceResult(value=dict(value))

        key_type, val_type = get_args(dtype)
        _results: dict[Any, Any] = {}
        batch = ErrorBatch(collect=self.collect_errors)
        for k, v in value.items():
            with batch.capture(segment=k):
                _key = self.hub(value=k, dtype=key_type)
                _val = self.hub(value=v, dtype=val_type)
                _results[_key] = _val
        batch.raise_if_any()
        return CoerceResult(value=_results)


__all__ = ["DictCoercerWorker"]
