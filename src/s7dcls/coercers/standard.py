from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from s7dcls.coercers.ops import FirstMatchCoercer
from s7dcls.coercers.protocol import (
    CoercerProtocol,
    JsonCoercerProtocol,
    StrictCoercerProtocol,
    StrictJsonCoercerProtocol,
)
from s7dcls.coercers.scaffold import RecursiveCoercer
from s7dcls.dataclass_hydrators.protocol import DataclassHydratorFactoryProtocol
from s7dcls.dataclass_hydrators.scaffold import ScaffoldDataclassHydratorFactory

from .mechanism import (
    AnnotatedCoercer,
    AnyCoercer,
    DataclassCoercer,
    DictCoercer,
    ListCoercer,
    LiteralCoercer,
    NoneCoercer,
    PathCoercer,
    StringBoolCoercer,
    StringJsonCoercer,
    StringNoneCoercer,
    StringTypeCallCoercer,
    TupleCoercer,
    TypeInstanceCoercer,
    UnionCoercer,
)


class StandardJsonCoercer(StrictJsonCoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_hydrator_factory: DataclassHydratorFactoryProtocol | None = None

        def build(self) -> StrictJsonCoercerProtocol:
            return StandardJsonCoercer(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardJsonCoercer.Args()
        hydrator_factory = (
            active_args.dataclass_hydrator_factory or ScaffoldDataclassHydratorFactory()
        )
        container_coercers: list[JsonCoercerProtocol] = []

        def build_coercer(inner: StrictCoercerProtocol) -> CoercerProtocol:
            containers: tuple[JsonCoercerProtocol, ...] = (
                DictCoercer(inner_coercer=inner),
                ListCoercer(inner_coercer=inner),
                TupleCoercer(inner_coercer=inner),
                DataclassCoercer(dataclass_hydrator=hydrator_factory(inner)),
            )
            container_coercers.extend(containers)
            return FirstMatchCoercer(
                coercers=(
                    AnyCoercer(),
                    AnnotatedCoercer(inner_coercer=inner),
                    UnionCoercer(inner_coercer=inner),
                    LiteralCoercer(inner_coercer=inner),
                    *containers,
                    NoneCoercer(),
                    TypeInstanceCoercer(datatype=bool),
                    TypeInstanceCoercer(datatype=int),
                    TypeInstanceCoercer(datatype=float),
                    TypeInstanceCoercer(datatype=str),
                    PathCoercer(),
                )
            )

        self.parent = RecursiveCoercer(coercer_recursion=build_coercer)
        self.container_coercers = tuple(container_coercers)

    def can_handle(self, *, dtype: Any) -> bool:
        return any(
            coercer.can_handle(dtype=dtype) for coercer in self.container_coercers
        )

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        return self.parent(value=value, dtype=dtype)


class StandardStringCoercer(StrictCoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_hydrator_factory: DataclassHydratorFactoryProtocol | None = None

        def build(self) -> StrictCoercerProtocol:
            return StandardStringCoercer(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardStringCoercer.Args()
        json_coercer = StandardJsonCoercer.Args(
            dataclass_hydrator_factory=active_args.dataclass_hydrator_factory,
        ).build()
        self.parent = RecursiveCoercer(
            coercer_recursion=lambda inner: FirstMatchCoercer(
                coercers=(
                    AnnotatedCoercer(inner_coercer=inner),
                    UnionCoercer(inner_coercer=inner),
                    LiteralCoercer(inner_coercer=inner),
                    StringBoolCoercer(),
                    StringTypeCallCoercer(datatype=int),
                    StringTypeCallCoercer(datatype=float),
                    StringTypeCallCoercer(datatype=Path),
                    StringJsonCoercer(json_coercer=json_coercer),
                    StringTypeCallCoercer(datatype=str),
                    StringNoneCoercer(),
                )
            )
        )

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        return self.parent(value=value, dtype=dtype)


__all__ = [
    "StandardJsonCoercer",
    "StandardStringCoercer",
]
