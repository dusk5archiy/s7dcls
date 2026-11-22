from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from s7dcls.coercers.protocol import StrictCoercerProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class DataclassHydratorProtocol(Protocol):
    def __call__[T: DataclassInstance](
        self,
        *,
        datacls: type[T],
        data: dict[str, Any],
        coercer: StrictCoercerProtocol,
        extra_keys_allowed: bool,
    ) -> T: ...


__all__ = ["DataclassHydratorProtocol"]
