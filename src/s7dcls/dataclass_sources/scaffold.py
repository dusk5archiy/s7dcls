from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from s7dcls.dataclass_kwargs_resolvers.protocol import DataclassKwargsResolverProtocol
from s7dcls.dict_fetchers.protocol import DictFetcherProtocol

from .protocol import DataclassSourceProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


@dataclass(kw_only=True, frozen=True)
class ChainDataclassSource(DataclassSourceProtocol):
    dict_fetcher: DictFetcherProtocol
    kwargs_resolver: DataclassKwargsResolverProtocol

    def __call__(self, *, datacls: type[DataclassInstance]) -> Mapping[str, Any]:
        return self.kwargs_resolver(data=self.dict_fetcher(), datacls=datacls)


__all__ = ["ChainDataclassSource"]
