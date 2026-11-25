from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from s7dcls.dataclass_kwargs_resolvers.scaffold import ScaffoldDataclassKwargsResolver
from s7dcls.protocols import TransformProtocol

from ..protocol import DataclassHydratorFactoryProtocol, DataclassHydratorProtocol
from ..scaffold import ScaffoldDataclassHydrator

if TYPE_CHECKING:
    from s7dcls.coercers.protocol import CoercerProtocol


class StandardDataclassHydratorFactory(DataclassHydratorFactoryProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        class_key_projection: TransformProtocol[str] | None = None
        extra_keys_allowed: bool = False
        collect_errors: bool = False

        def build(self) -> StandardDataclassHydratorFactory:
            return StandardDataclassHydratorFactory(self)

    def __init__(self, args: Args | None = None) -> None:
        self.args = args or StandardDataclassHydratorFactory.Args()

    def __call__(self, coercer: CoercerProtocol) -> DataclassHydratorProtocol:
        return ScaffoldDataclassHydrator(
            kwargs_resolver=ScaffoldDataclassKwargsResolver(
                coercer=coercer,
                class_key_projection=self.args.class_key_projection,
                extra_keys_allowed=self.args.extra_keys_allowed,
                collect_errors=self.args.collect_errors,
            ),
            collect_errors=self.args.collect_errors,
        )


__all__ = ["StandardDataclassHydratorFactory"]
