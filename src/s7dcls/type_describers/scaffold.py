from __future__ import annotations

from typing import Any

from .protocol import StrictTypeDescriberProtocol, TypeDescriberRecursionProtocol


class RecursiveTypeDescriber(StrictTypeDescriberProtocol):
    def __init__(self, *, describer_recursion: TypeDescriberRecursionProtocol) -> None:
        self.describer = describer_recursion(self)

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        result = self.describer(dtype=dtype)
        if result is not None:
            return result.schema
        raise TypeError({"dtype": str(dtype)})


__all__ = ["RecursiveTypeDescriber"]
