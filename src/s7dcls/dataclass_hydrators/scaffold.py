from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from s7dcls.dataclass_kwargs_resolvers.protocol import DataclassKwargsResolverProtocol
from s7dcls.dataclass_kwargs_resolvers.scaffold import ScaffoldDataclassKwargsResolver
from s7dcls.type_emitters.protocol import TransformProtocol

from .protocol import DataclassHydratorFactoryProtocol, DataclassHydratorProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from s7dcls.coercers.protocol import CoercerProtocol


@dataclass(kw_only=True, frozen=True)
class ChainDataclassHydrator(DataclassHydratorProtocol):
    kwargs_resolver: DataclassKwargsResolverProtocol

    def __call__[T: DataclassInstance](
        self,
        *,
        data: Mapping[str, Any],
        datacls: type[T],
    ) -> T:
        return datacls(**self.kwargs_resolver(data=data, datacls=datacls))


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassHydratorFactory(DataclassHydratorFactoryProtocol):
    class_key_projection: TransformProtocol[str] | None = None
    data_key_projection: TransformProtocol[str] | None = None
    extra_keys_allowed: bool = False

    def __call__(self, coercer: CoercerProtocol) -> DataclassHydratorProtocol:
        return ChainDataclassHydrator(
            kwargs_resolver=ScaffoldDataclassKwargsResolver(
                coercer=coercer,
                class_key_projection=self.class_key_projection,
                data_key_projection=self.data_key_projection,
                extra_keys_allowed=self.extra_keys_allowed,
            )
        )


__all__ = ["ChainDataclassHydrator", "ScaffoldDataclassHydratorFactory"]
