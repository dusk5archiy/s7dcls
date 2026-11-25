from __future__ import annotations

from typing import Any, Protocol


class SchemaDescriberProtocol(Protocol):
    def __call__(self, *, dtype: Any) -> dict[str, Any]: ...


__all__ = ["SchemaDescriberProtocol"]
