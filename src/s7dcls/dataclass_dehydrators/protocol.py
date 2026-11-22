from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from s7dcls.uncoercers.protocol import StrictUncoercerProtocol


class DataclassDehydratorProtocol(Protocol):
    def __call__(
        self,
        *,
        instance: DataclassInstance,
        uncoercer: StrictUncoercerProtocol,
    ) -> dict[str, Any]: ...


__all__ = ["DataclassDehydratorProtocol"]
