from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from s7dcls.coercers.ops import FirstMatchCoercerWorker
from s7dcls.coercers.protocol import (
    CoercerProtocol,
    CoercerWorkerProtocol,
    JsonCoercerProtocol,
    JsonCoercerWorkerProtocol,
)
from s7dcls.coercers.scaffold import HubCoercer
from s7dcls.dataclass_hydrators.protocol import DataclassHydratorFactoryProtocol
from s7dcls.dataclass_hydrators.scaffold import ScaffoldDataclassHydratorFactory

from .mechanism import (
    AnnotatedCoercerWorker,
    AnyCoercerWorker,
    DataclassCoercerWorker,
    DictCoercerWorker,
    ListCoercerWorker,
    LiteralCoercerWorker,
    NoneCoercerWorker,
    PathCoercerWorker,
    StringBoolCoercerWorker,
    StringJsonCoercerWorker,
    StringNoneCoercerWorker,
    StringTypeCallCoercerWorker,
    TupleCoercerWorker,
    TypeInstanceCoercerWorker,
    UnionCoercerWorker,
)


class StandardJsonCoercer(JsonCoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_hydrator_factory: DataclassHydratorFactoryProtocol | None = None

        def build(self) -> JsonCoercerProtocol:
            return StandardJsonCoercer(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardJsonCoercer.Args()
        hydrator_factory = (
            active_args.dataclass_hydrator_factory or ScaffoldDataclassHydratorFactory()
        )
        container_workers: list[JsonCoercerWorkerProtocol] = []

        def spawn_worker(hub: CoercerProtocol) -> CoercerWorkerProtocol:
            containers: tuple[JsonCoercerWorkerProtocol, ...] = (
                DictCoercerWorker(hub=hub),
                ListCoercerWorker(hub=hub),
                TupleCoercerWorker(hub=hub),
                DataclassCoercerWorker(dataclass_hydrator=hydrator_factory(hub)),
            )
            container_workers.extend(containers)
            return FirstMatchCoercerWorker(
                workers=(
                    AnyCoercerWorker(),
                    AnnotatedCoercerWorker(hub=hub),
                    UnionCoercerWorker(hub=hub),
                    LiteralCoercerWorker(hub=hub),
                    *containers,
                    NoneCoercerWorker(),
                    TypeInstanceCoercerWorker(datatype=bool),
                    TypeInstanceCoercerWorker(datatype=int),
                    TypeInstanceCoercerWorker(datatype=float),
                    TypeInstanceCoercerWorker(datatype=str),
                    PathCoercerWorker(),
                )
            )

        self.parent = HubCoercer(spawner=spawn_worker)
        self.container_workers = tuple(container_workers)

    def can_handle(self, *, dtype: Any) -> bool:
        return any(worker.can_handle(dtype=dtype) for worker in self.container_workers)

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        return self.parent(value=value, dtype=dtype)


class StandardStringCoercer(CoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_hydrator_factory: DataclassHydratorFactoryProtocol | None = None

        def build(self) -> CoercerProtocol:
            return StandardStringCoercer(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardStringCoercer.Args()
        json_coercer = StandardJsonCoercer.Args(
            dataclass_hydrator_factory=active_args.dataclass_hydrator_factory,
        ).build()
        self.parent = HubCoercer(
            spawner=lambda hub: FirstMatchCoercerWorker(
                workers=(
                    AnnotatedCoercerWorker(hub=hub),
                    UnionCoercerWorker(hub=hub),
                    LiteralCoercerWorker(hub=hub),
                    StringBoolCoercerWorker(),
                    StringTypeCallCoercerWorker(datatype=int),
                    StringTypeCallCoercerWorker(datatype=float),
                    StringTypeCallCoercerWorker(datatype=Path),
                    StringJsonCoercerWorker(json_coercer=json_coercer),
                    StringTypeCallCoercerWorker(datatype=str),
                    StringNoneCoercerWorker(),
                )
            )
        )

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        return self.parent(value=value, dtype=dtype)


__all__ = [
    "StandardJsonCoercer",
    "StandardStringCoercer",
]
