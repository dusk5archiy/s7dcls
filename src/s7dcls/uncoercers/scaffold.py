from __future__ import annotations

from typing import Any

from .protocol import StrictUncoercerProtocol, UncoercerRecursionProtocol


class RecursiveUncoercer(StrictUncoercerProtocol):
    def __init__(self, *, uncoercer_recursion: UncoercerRecursionProtocol) -> None:
        self.uncoercer = uncoercer_recursion(self)

    def __call__(self, *, value: Any) -> Any:
        result = self.uncoercer(value=value)
        if result is not None:
            return result.value
        raise TypeError({"value": value, "got_type": str(type(value))})


__all__ = ["RecursiveUncoercer"]
