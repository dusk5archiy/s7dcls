from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from .mechanism import (
    AnnotatedValidatorWorker,
    AnyValidatorWorker,
    DataclassValidatorWorker,
    DateTimeValidatorWorker,
    DictValidatorWorker,
    EnumValidatorWorker,
    ListValidatorWorker,
    LiteralValidatorWorker,
    NoneValidatorWorker,
    SetValidatorWorker,
    TaggedUnionValidatorWorker,
    TupleValidatorWorker,
    TypeAliasValidatorWorker,
    TypeInstanceValidatorWorker,
    UnionValidatorWorker,
)
from .ops import FirstMatchValidatorWorker
from .protocol import ValidatorProtocol
from .scaffold import HubValidator


class StandardValidator(ValidatorProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        collect_errors: bool = False

        def build(self) -> StandardValidator:
            return StandardValidator(self)

    def __init__(self, args: Args | None = None) -> None:
        self.args = args or StandardValidator.Args()
        collect = self.args.collect_errors
        self.parent = HubValidator(
            spawner=lambda hub: FirstMatchValidatorWorker(
                workers=(
                    TypeAliasValidatorWorker(hub=hub),
                    AnyValidatorWorker(),
                    AnnotatedValidatorWorker(hub=hub),
                    TaggedUnionValidatorWorker(hub=hub),
                    UnionValidatorWorker(hub=hub),
                    LiteralValidatorWorker(),
                    NoneValidatorWorker(),
                    EnumValidatorWorker(),
                    DateTimeValidatorWorker(),
                    TypeInstanceValidatorWorker(datatype=bool),
                    TypeInstanceValidatorWorker(datatype=int),
                    TypeInstanceValidatorWorker(datatype=float),
                    TypeInstanceValidatorWorker(datatype=str),
                    TypeInstanceValidatorWorker(datatype=Path),
                    TypeInstanceValidatorWorker(datatype=UUID),
                    TypeInstanceValidatorWorker(datatype=Decimal),
                    ListValidatorWorker(hub=hub, collect_errors=collect),
                    SetValidatorWorker(hub=hub, collect_errors=collect),
                    DictValidatorWorker(hub=hub, collect_errors=collect),
                    TupleValidatorWorker(hub=hub, collect_errors=collect),
                    DataclassValidatorWorker(hub=hub, collect_errors=collect),
                )
            )
        )

    def __call__(self, *, value: Any, dtype: Any) -> None:
        self.parent(value=value, dtype=dtype)


__all__ = ["StandardValidator"]
