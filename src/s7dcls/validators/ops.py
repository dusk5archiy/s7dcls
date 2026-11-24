from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .models import ValidateResult
from .protocol import ValidatorProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchValidator(ValidatorProtocol):
    validators: Sequence[ValidatorProtocol]

    def __call__(self, *, value: Any, dtype: Any) -> ValidateResult | None:
        for validator in self.validators:
            result = validator(value=value, dtype=dtype)
            if result is not None:
                return result
        return None


__all__ = ["FirstMatchValidator"]
