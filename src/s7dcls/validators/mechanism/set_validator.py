from __future__ import annotations

from dataclasses import dataclass
from typing import Any, get_args, get_origin

from s7dcls.error_paths import ErrorBatch

from ..models import ValidateResult
from ..protocol import ValidatorProtocol, ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class SetValidatorWorker(ValidatorWorkerProtocol):
    hub: ValidatorProtocol
    collect_errors: bool = False

    def __call__(self, *, value, dtype):
        origin = get_origin(dtype)
        target: Any = origin if origin in (set, frozenset) else dtype
        if target not in (set, frozenset):
            return None

        if not isinstance(value, target):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(target),
                    "got_type": str(type(value)),
                }
            )

        if origin is None:
            return ValidateResult()

        elem_type = get_args(dtype)[0]
        batch = ErrorBatch(collect=self.collect_errors)
        for idx, item in enumerate(value):
            with batch.capture(segment=idx):
                self.hub(value=item, dtype=elem_type)
        batch.raise_if_any()
        return ValidateResult()


__all__ = ["SetValidatorWorker"]
