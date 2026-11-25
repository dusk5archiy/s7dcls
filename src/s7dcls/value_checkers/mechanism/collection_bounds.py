from __future__ import annotations

from collections.abc import Iterable, Sized
from dataclasses import dataclass
from typing import Any

from ..protocol import ValueCheckerProtocol


def _require_sized(value: Any) -> Sized:
    if not isinstance(value, Sized):
        raise TypeError(
            {
                "value": value,
                "expected_type": str(Sized),
                "got_type": str(type(value)),
            }
        )
    return value


@dataclass(kw_only=True, frozen=True)
class MinLen(ValueCheckerProtocol):
    limit: int

    def __call__(self, value: Any) -> None:
        sized = _require_sized(value)
        length = len(sized)
        if length < self.limit:
            raise ValueError(
                {
                    "value": value,
                    "length": length,
                    "constraint": f"len >= {self.limit}",
                }
            )


@dataclass(kw_only=True, frozen=True)
class MaxLen(ValueCheckerProtocol):
    limit: int

    def __call__(self, value: Any) -> None:
        sized = _require_sized(value)
        length = len(sized)
        if length > self.limit:
            raise ValueError(
                {
                    "value": value,
                    "length": length,
                    "constraint": f"len <= {self.limit}",
                }
            )


@dataclass(kw_only=True, frozen=True)
class UniqueItems(ValueCheckerProtocol):
    def __call__(self, value: Any) -> None:
        if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(Iterable),
                    "got_type": str(type(value)),
                }
            )
        seen: list[Any] = []
        for item in value:
            if any(item == prev and type(item) is type(prev) for prev in seen):
                raise ValueError(
                    {"value": value, "duplicate": item, "constraint": "unique"}
                )
            seen.append(item)


__all__ = ["MaxLen", "MinLen", "UniqueItems"]
