from __future__ import annotations

from typing import Any

from .protocol import CoercerRecursionProtocol, StrictCoercerProtocol


class RecursiveCoercer(StrictCoercerProtocol):
    def __init__(self, *, coercer_recursion: CoercerRecursionProtocol) -> None:
        self.coercer = coercer_recursion(self)

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        result = self.coercer(value=value, dtype=dtype)
        if result is not None:
            return result.value
        raise TypeError({"value": value, "expected_type": str(dtype)})


__all__ = ["RecursiveCoercer"]
