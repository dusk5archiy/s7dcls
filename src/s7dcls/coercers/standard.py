from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAliasType

from s7dcls.coercers.ops import FirstMatchCoercerWorker
from s7dcls.coercers.protocol import (
    CoercerProtocol,
    CoercerWorkerProtocol,
    JsonCoercerProtocol,
    JsonCoercerWorkerProtocol,
)
from s7dcls.coercers.scaffold import HubCoercer
from s7dcls.dataclass_hydrators.protocol import DataclassHydratorFactoryProtocol
from s7dcls.dataclass_hydrators.standard.factory import (
    StandardDataclassHydratorFactory,
)

from .mechanism import (
    AnnotatedCoercerWorker,
    AnyCoercerWorker,
    DataclassCoercerWorker,
    DateTimeCoercerWorker,
    DecimalCoercerWorker,
    DictCoercerWorker,
    EnumCoercerWorker,
    ListCoercerWorker,
    LiteralCoercerWorker,
    NoneCoercerWorker,
    PathCoercerWorker,
    SetCoercerWorker,
    StringBoolCoercerWorker,
    StringEnumCoercerWorker,
    StringJsonCoercerWorker,
    StringNoneCoercerWorker,
    StringTimedeltaCoercerWorker,
    StringTypeCallCoercerWorker,
    TaggedUnionCoercerWorker,
    TupleCoercerWorker,
    TypeAliasCoercerWorker,
    TypeInstanceCoercerWorker,
    UnionCoercerWorker,
    UuidCoercerWorker,
)


class StandardJsonCoercer(JsonCoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_hydrator_factory: DataclassHydratorFactoryProtocol | None = None
        collect_errors: bool = False

        def build(self) -> JsonCoercerProtocol:
            return StandardJsonCoercer(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardJsonCoercer.Args()
        collect = active_args.collect_errors
        hydrator_factory = (
            active_args.dataclass_hydrator_factory
            or StandardDataclassHydratorFactory.Args(collect_errors=collect).build()
        )
        container_workers: list[JsonCoercerWorkerProtocol] = []

        def spawn_worker(hub: CoercerProtocol) -> CoercerWorkerProtocol:
            tagged_union_worker = TaggedUnionCoercerWorker(hub=hub)
            containers: tuple[JsonCoercerWorkerProtocol, ...] = (
                DictCoercerWorker(hub=hub, collect_errors=collect),
                ListCoercerWorker(hub=hub, collect_errors=collect),
                TupleCoercerWorker(hub=hub, collect_errors=collect),
                SetCoercerWorker(hub=hub, collect_errors=collect),
                DataclassCoercerWorker(dataclass_hydrator=hydrator_factory(hub)),
            )
            container_workers.extend((tagged_union_worker, *containers))
            return FirstMatchCoercerWorker(
                workers=(
                    TypeAliasCoercerWorker(hub=hub),
                    AnyCoercerWorker(),
                    AnnotatedCoercerWorker(hub=hub),
                    tagged_union_worker,
                    UnionCoercerWorker(hub=hub),
                    LiteralCoercerWorker(hub=hub),
                    *containers,
                    NoneCoercerWorker(),
                    EnumCoercerWorker(),
                    TypeInstanceCoercerWorker(datatype=bool),
                    TypeInstanceCoercerWorker(datatype=int),
                    TypeInstanceCoercerWorker(datatype=float),
                    TypeInstanceCoercerWorker(datatype=str),
                    PathCoercerWorker(),
                    UuidCoercerWorker(),
                    DateTimeCoercerWorker(),
                    DecimalCoercerWorker(),
                )
            )

        self.parent = HubCoercer.Args(spawner=spawn_worker).build()
        self.container_workers = tuple(container_workers)

    def can_handle(self, *, dtype: Any) -> bool:
        while isinstance(dtype, TypeAliasType):
            dtype = dtype.__value__
        return any(worker.can_handle(dtype=dtype) for worker in self.container_workers)

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        return self.parent(value=value, dtype=dtype)


class StandardStringCoercer(CoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_hydrator_factory: DataclassHydratorFactoryProtocol | None = None
        collect_errors: bool = False

        def build(self) -> CoercerProtocol:
            return StandardStringCoercer(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardStringCoercer.Args()
        json_coercer = StandardJsonCoercer.Args(
            dataclass_hydrator_factory=active_args.dataclass_hydrator_factory,
            collect_errors=active_args.collect_errors,
        ).build()
        self.parent = HubCoercer.Args(
            spawner=lambda hub: FirstMatchCoercerWorker(
                workers=(
                    TypeAliasCoercerWorker(hub=hub),
                    AnnotatedCoercerWorker(hub=hub),
                    UnionCoercerWorker(hub=hub),
                    LiteralCoercerWorker(hub=hub),
                    StringEnumCoercerWorker(hub=hub),
                    StringBoolCoercerWorker(),
                    StringTypeCallCoercerWorker(datatype=int),
                    StringTypeCallCoercerWorker(datatype=float),
                    StringTypeCallCoercerWorker(datatype=Path),
                    UuidCoercerWorker(),
                    StringTimedeltaCoercerWorker(),
                    DateTimeCoercerWorker(),
                    DecimalCoercerWorker(),
                    StringJsonCoercerWorker(json_coercer=json_coercer),
                    StringTypeCallCoercerWorker(datatype=str),
                    StringNoneCoercerWorker(),
                )
            )
        ).build()

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        return self.parent(value=value, dtype=dtype)


__all__ = [
    "StandardJsonCoercer",
    "StandardStringCoercer",
]
