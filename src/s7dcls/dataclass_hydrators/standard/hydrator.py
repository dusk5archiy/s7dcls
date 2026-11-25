from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from s7dcls.dataclass_kwargs_resolvers.scaffold import ScaffoldDataclassKwargsResolver

from ..protocol import DataclassHydratorProtocol
from ..scaffold import ScaffoldDataclassHydrator

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from s7dcls.coercers.protocol import CoercerProtocol


class StandardDataclassHydrator(DataclassHydratorProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        coercer: CoercerProtocol | None = None
        collect_errors: bool = False

        def build(self) -> StandardDataclassHydrator:
            return StandardDataclassHydrator(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardDataclassHydrator.Args()
        coercer = active_args.coercer
        if coercer is None:
            from s7dcls.coercers.standard import StandardJsonCoercer

            coercer = StandardJsonCoercer.Args(
                collect_errors=active_args.collect_errors
            ).build()

        self.parent = ScaffoldDataclassHydrator(
            kwargs_resolver=ScaffoldDataclassKwargsResolver(
                coercer=coercer,
                collect_errors=active_args.collect_errors,
            ),
            collect_errors=active_args.collect_errors,
        )

    def __call__[T: DataclassInstance](
        self, *, data: Mapping[str, Any], datacls: type[T]
    ) -> T:
        return self.parent(data=data, datacls=datacls)


__all__ = ["StandardDataclassHydrator"]
