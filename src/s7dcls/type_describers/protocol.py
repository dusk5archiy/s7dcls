from __future__ import annotations

from typing import Any, Protocol

from .models import DescribeTypeResult


class TypeDescriberWorkerProtocol(Protocol):
    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None: ...


class TypeDescriberProtocol(Protocol):
    def __call__(self, *, dtype: Any) -> dict[str, Any]: ...


class TypeDescriberSpawnerProtocol(Protocol):
    def __call__(
        self, hub: TypeDescriberProtocol, /
    ) -> TypeDescriberWorkerProtocol: ...


__all__ = [
    "TypeDescriberProtocol",
    "TypeDescriberSpawnerProtocol",
    "TypeDescriberWorkerProtocol",
]
