from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ..protocol import ValueCheckerProtocol


def _require_number(value: Any) -> int | float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(
            {
                "value": value,
                "expected_type": str(int | float),
                "got_type": str(type(value)),
            }
        )
    return value


@dataclass(kw_only=True, frozen=True)
class Gt(ValueCheckerProtocol):
    limit: int | float

    def __call__(self, value) -> None:
        num = _require_number(value)
        if not (num > self.limit):
            raise ValueError({"value": value, "constraint": f"> {self.limit}"})


@dataclass(kw_only=True, frozen=True)
class Ge(ValueCheckerProtocol):
    limit: int | float

    def __call__(self, value) -> None:
        num = _require_number(value)
        if not (num >= self.limit):
            raise ValueError({"value": value, "constraint": f">= {self.limit}"})


@dataclass(kw_only=True, frozen=True)
class Lt(ValueCheckerProtocol):
    limit: int | float

    def __call__(self, value) -> None:
        num = _require_number(value)
        if not (num < self.limit):
            raise ValueError({"value": value, "constraint": f"< {self.limit}"})


@dataclass(kw_only=True, frozen=True)
class Le(ValueCheckerProtocol):
    limit: int | float

    def __call__(self, value) -> None:
        num = _require_number(value)
        if not (num <= self.limit):
            raise ValueError({"value": value, "constraint": f"<= {self.limit}"})


@dataclass(kw_only=True, frozen=True)
class MultipleOf(ValueCheckerProtocol):
    step: int | float

    def __post_init__(self) -> None:
        if self.step == 0:
            raise ValueError({"step": self.step, "constraint": "!= 0"})

    def __call__(self, value) -> None:
        num = _require_number(value)
        if Decimal(str(num)) % Decimal(str(self.step)) != 0:
            raise ValueError({"value": value, "constraint": f"% {self.step} == 0"})


__all__ = ["Ge", "Gt", "Le", "Lt", "MultipleOf"]
