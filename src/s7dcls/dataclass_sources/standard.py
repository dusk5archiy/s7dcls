from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from s7dcls.dataclass_kwargs_resolvers.scaffold import ScaffoldDataclassKwargsResolver
from s7dcls.dict_fetchers.protocol import DictFetcherProtocol

from .protocol import DataclassSourceProtocol
from .scaffold import ChainDataclassSource

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from s7dcls.coercers.protocol import StrictCoercerProtocol


class StandardDataclassSource(DataclassSourceProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dict_fetcher: DictFetcherProtocol
        coercer: StrictCoercerProtocol | None = None

        def build(self) -> StandardDataclassSource:
            return StandardDataclassSource(self)

    def __init__(self, args: Args) -> None:
        coercer = args.coercer
        if coercer is None:
            from s7dcls.coercers.standard import StandardJsonCoercer

            coercer = StandardJsonCoercer.Args().build()

        self.parent = ChainDataclassSource(
            dict_fetcher=args.dict_fetcher,
            kwargs_resolver=ScaffoldDataclassKwargsResolver(coercer=coercer),
        )

    def __call__(self, *, datacls: type[DataclassInstance]) -> Mapping[str, Any]:
        return self.parent(datacls=datacls)


__all__ = ["StandardDataclassSource"]
