from __future__ import annotations

from typing import Any, Protocol

from .models import DescribeTypeResult


class TypeDescriberProtocol(Protocol):
    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None: ...


class StrictTypeDescriberProtocol(Protocol):
    def __call__(self, *, dtype: Any) -> dict[str, Any]: ...


class TypeDescriberRecursionProtocol(Protocol):
    def __call__(
        self, inner_type_describer: StrictTypeDescriberProtocol, /
    ) -> TypeDescriberProtocol: ...


__all__ = [
    "StrictTypeDescriberProtocol",
    "TypeDescriberProtocol",
    "TypeDescriberRecursionProtocol",
]
