from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from s7dcls.coercers.protocol import CoercerProtocol


class DataclassHydratorProtocol(Protocol):
    def __call__[T: DataclassInstance](
        self,
        *,
        data: Mapping[str, Any],
        datacls: type[T],
    ) -> T: ...


class DataclassHydratorFactoryProtocol(Protocol):
    def __call__(self, coercer: CoercerProtocol, /) -> DataclassHydratorProtocol: ...


__all__ = ["DataclassHydratorFactoryProtocol", "DataclassHydratorProtocol"]
