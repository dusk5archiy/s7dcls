from __future__ import annotations

from dataclasses import dataclass
from typing import get_args, get_origin

from s7dcls.error_paths import ErrorBatch

from ..models import ValidateResult
from ..protocol import ValidatorProtocol, ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class TupleValidatorWorker(ValidatorWorkerProtocol):
    hub: ValidatorProtocol
    collect_errors: bool = False

    def __call__(self, *, value, dtype):
        if dtype is not tuple and get_origin(dtype) is not tuple:
            return None

        if not isinstance(value, tuple):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(tuple),
                    "got_type": str(type(value)),
                }
            )

        if get_origin(dtype) is None:
            return ValidateResult()

        args = get_args(dtype)
        if len(args) == 2 and args[1] is Ellipsis:
            elem_type = args[0]
            batch = ErrorBatch(collect=self.collect_errors)
            for idx, item in enumerate(value):
                with batch.capture(segment=idx):
                    self.hub(value=item, dtype=elem_type)
            batch.raise_if_any()
            return ValidateResult()

        if len(args) == 1 and args[0] == ():
            if value:
                raise ValueError({"value": value, "expected_type": str(dtype)})
            return ValidateResult()

        if len(value) != len(args):
            raise ValueError({"value": value, "expected_type": str(dtype)})

        batch = ErrorBatch(collect=self.collect_errors)
        for idx, (item, arg_type) in enumerate(zip(value, args, strict=True)):
            with batch.capture(segment=idx):
                self.hub(value=item, dtype=arg_type)
        batch.raise_if_any()
        return ValidateResult()


__all__ = ["TupleValidatorWorker"]
