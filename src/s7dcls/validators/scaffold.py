from __future__ import annotations

from typing import Any

from .protocol import StrictValidatorProtocol, ValidatorRecursionProtocol


class RecursiveValidator(StrictValidatorProtocol):
    def __init__(self, *, validator_recursion: ValidatorRecursionProtocol) -> None:
        self.validator = validator_recursion(self)

    def __call__(self, *, value: Any, dtype: Any) -> None:
        result = self.validator(value=value, dtype=dtype)
        if result is not None:
            return
        raise TypeError({"value": value, "expected_type": str(dtype)})


__all__ = ["RecursiveValidator"]
