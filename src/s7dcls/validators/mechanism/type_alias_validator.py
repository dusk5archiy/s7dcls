from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAliasType

from ..models import ValidateResult
from ..protocol import ValidatorProtocol, ValidatorWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class TypeAliasValidatorWorker(ValidatorWorkerProtocol):
    hub: ValidatorProtocol

    def __call__(self, *, value, dtype):
        if isinstance(dtype, TypeAliasType):
            self.hub(value=value, dtype=dtype.__value__)
            return ValidateResult()
        return None


__all__ = ["TypeAliasValidatorWorker"]
