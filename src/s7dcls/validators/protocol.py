from __future__ import annotations

from typing import Any, Protocol

from .models import ValidateResult


class ValidatorProtocol(Protocol):
    def __call__(self, *, value: Any, dtype: Any) -> ValidateResult | None: ...


class StrictValidatorProtocol(Protocol):
    def __call__(self, *, value: Any, dtype: Any) -> None: ...


class ValidatorRecursionProtocol(Protocol):
    def __call__(
        self, inner_validator: StrictValidatorProtocol, /
    ) -> ValidatorProtocol: ...


__all__ = [
    "StrictValidatorProtocol",
    "ValidatorProtocol",
    "ValidatorRecursionProtocol",
]
