from __future__ import annotations

from dataclasses import dataclass, fields

from s7dcls.error_paths import ErrorBatch
from s7dcls.type_hints import resolve_dataclass_type

from ..models import ValidateResult
from ..protocol import ValidatorProtocol, ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class DataclassValidatorWorker(ValidatorWorkerProtocol):
    hub: ValidatorProtocol
    collect_errors: bool = False

    def __call__(self, *, value, dtype):
        resolved = resolve_dataclass_type(dtype)
        if resolved is None:
            return None

        actual_cls, type_hints = resolved
        if not isinstance(value, actual_cls):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(dtype),
                    "got_type": str(type(value)),
                }
            )

        batch = ErrorBatch(collect=self.collect_errors)
        for definition in fields(actual_cls):
            if not definition.init:
                continue
            field_dtype = type_hints.get(definition.name, definition.type)
            field_value = getattr(value, definition.name)
            with batch.capture(segment=definition.name):
                self.hub(value=field_value, dtype=field_dtype)
        batch.raise_if_any()
        return ValidateResult()


__all__ = ["DataclassValidatorWorker"]
