from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .protocol import ValueCheckerProtocol


@dataclass(kw_only=True, frozen=True)
class AllValueChecker(ValueCheckerProtocol):
    checkers: Sequence[ValueCheckerProtocol] = ()

    def __call__(self, value: Any, /) -> None:
        for checker in self.checkers:
            checker(value)


@dataclass(kw_only=True, frozen=True)
class AnyValueChecker(ValueCheckerProtocol):
    checkers: Sequence[ValueCheckerProtocol]

    def __call__(self, value: Any, /) -> None:
        errors: list[Exception] = []
        for checker in self.checkers:
            try:
                checker(value)
                return
            except (TypeError, ValueError) as e:
                errors.append(e)

        if errors:
            if any(isinstance(e, ValueError) for e in errors):
                raise ValueError({"value": value, "errors": errors}) from errors[-1]
            raise TypeError({"value": value, "errors": errors}) from errors[-1]

        raise ValueError({"value": value, "errors": []})


__all__ = ["AllValueChecker", "AnyValueChecker"]
