from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class DataclassKwargsResolverProtocol(Protocol):
    def __call__(
        self,
        *,
        data: Mapping[str, Any],
        datacls: type[DataclassInstance],
    ) -> Mapping[str, Any]: ...


__all__ = ["DataclassKwargsResolverProtocol"]
