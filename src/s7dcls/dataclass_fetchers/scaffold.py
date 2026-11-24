from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from s7dcls.dataclass_sources.protocol import DataclassSourceProtocol
from s7dcls.type_emitters.protocol import DataclassEmitterProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


@dataclass(kw_only=True, frozen=True)
class ChainDataclassFetcher[T: DataclassInstance](DataclassEmitterProtocol[T]):
    source: DataclassSourceProtocol
    datacls: type[T]

    def __call__(self) -> T:
        return self.datacls(**self.source(datacls=self.datacls))


__all__ = ["ChainDataclassFetcher"]
