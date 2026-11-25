from __future__ import annotations

from typing import Any, Protocol

from .models import ValidateResult


class ValidatorWorkerProtocol(Protocol):
    def __call__(self, *, value: Any, dtype: Any) -> ValidateResult | None: ...


class ValidatorProtocol(Protocol):
    def __call__(self, *, value: Any, dtype: Any) -> None: ...


class ValidatorSpawnerProtocol(Protocol):
    def __call__(self, hub: ValidatorProtocol, /) -> ValidatorWorkerProtocol: ...


__all__ = [
    "ValidatorProtocol",
    "ValidatorSpawnerProtocol",
    "ValidatorWorkerProtocol",
]
