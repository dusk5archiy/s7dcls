from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, JsonCoercerWorkerProtocol
from s7dcls.error_paths import ErrorBatch


@dataclass(kw_only=True, frozen=True)
class TupleCoercerWorker(JsonCoercerWorkerProtocol):
    hub: CoercerProtocol
    collect_errors: bool = False

    def can_handle(self, *, dtype: Any) -> bool:
        return dtype is tuple or get_origin(dtype) is tuple

    def __call__(
        self, *, value: Any, dtype: Any
    ) -> CoerceResult[tuple[Any, ...]] | None:
        if dtype is not tuple and get_origin(dtype) is not tuple:
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
            return CoerceResult(value=tuple(value))

        args = get_args(dtype)
        if len(args) == 2 and args[1] is Ellipsis:
            _dtype = args[0]
            _results: list[Any] = []
            batch = ErrorBatch(collect=self.collect_errors)
            for idx, item in enumerate(value):
                with batch.capture(segment=idx):
                    _results.append(self.hub(value=item, dtype=_dtype))
            batch.raise_if_any()
            return CoerceResult(value=tuple(_results))

        if len(args) == 1 and args[0] == ():
            if value:
                raise ValueError({"value": value, "expected_type": str(dtype)})
            return CoerceResult(value=())

        if len(value) != len(args):
            raise ValueError({"value": value, "expected_type": str(dtype)})

        _fixed_results: list[Any] = []
        batch = ErrorBatch(collect=self.collect_errors)
        for idx, (item, arg_type) in enumerate(zip(value, args, strict=True)):
            with batch.capture(segment=idx):
                _fixed_results.append(self.hub(value=item, dtype=arg_type))
        batch.raise_if_any()
        return CoerceResult(value=tuple(_fixed_results))


__all__ = ["TupleCoercerWorker"]
