from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from s7dcls.dict_transforms.protocol import DictTransformProtocol

from .protocol import DictFetcherProtocol


@dataclass(kw_only=True, frozen=True)
class AggregateDictFetcher(DictFetcherProtocol):
    dict_fetchers: Sequence[DictFetcherProtocol]

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for dict_fetcher in self.dict_fetchers:
            for k, v in dict_fetcher().items():
                data[k] = v
        return data


@dataclass(kw_only=True, frozen=True)
class DecoratedDictFetcher(DictFetcherProtocol):
    dict_fetcher: DictFetcherProtocol
    dict_transform: DictTransformProtocol

    def __call__(self) -> dict[str, Any]:
        return self.dict_transform(self.dict_fetcher())


__all__ = ["AggregateDictFetcher", "DecoratedDictFetcher"]
