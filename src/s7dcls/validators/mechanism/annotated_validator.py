from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, get_args, get_origin

from s7dcls.value_checkers.protocol import ValueCheckerProtocol

from ..models import ValidateResult
from ..protocol import ValidatorProtocol, ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class AnnotatedValidatorWorker(ValidatorWorkerProtocol):
    hub: ValidatorProtocol

    def __call__(self, *, value, dtype):
        if get_origin(dtype) is not Annotated:
            return None

        base_type, *extras = get_args(dtype)
        self.hub(value=value, dtype=base_type)

        for extra in extras:
            if isinstance(extra, ValueCheckerProtocol):
                extra(value)

        return ValidateResult()


__all__ = ["AnnotatedValidatorWorker"]
