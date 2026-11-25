from __future__ import annotations

from dataclasses import dataclass
from typing import get_args, get_origin

from s7dcls.error_paths import ErrorBatch

from ..models import ValidateResult
from ..protocol import ValidatorProtocol, ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class ListValidatorWorker(ValidatorWorkerProtocol):
    hub: ValidatorProtocol
    collect_errors: bool = False

    def __call__(self, *, value, dtype):
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
            return ValidateResult()

        elem_type = get_args(dtype)[0]
        batch = ErrorBatch(collect=self.collect_errors)
        for idx, item in enumerate(value):
            with batch.capture(segment=idx):
                self.hub(value=item, dtype=elem_type)
        batch.raise_if_any()
        return ValidateResult()


__all__ = ["ListValidatorWorker"]
