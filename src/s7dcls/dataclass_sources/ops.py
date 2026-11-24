from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .protocol import DataclassSourceProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


@dataclass(kw_only=True, frozen=True)
class AggregateDataclassSource(DataclassSourceProtocol):
    sources: Sequence[DataclassSourceProtocol]

    def __call__(self, *, datacls: type[DataclassInstance]) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        for source in self.sources:
            kwargs.update(source(datacls=datacls))
        return kwargs


__all__ = ["AggregateDataclassSource"]
