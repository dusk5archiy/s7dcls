from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mechanism import (
    AnnotatedValidatorWorker,
    AnyValidatorWorker,
    DataclassValidatorWorker,
    DictValidatorWorker,
    ListValidatorWorker,
    LiteralValidatorWorker,
    NoneValidatorWorker,
    TupleValidatorWorker,
    TypeInstanceValidatorWorker,
    UnionValidatorWorker,
)
from .ops import FirstMatchValidatorWorker
from .protocol import ValidatorProtocol
from .scaffold import HubValidator


class StandardValidator(ValidatorProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        def build(self) -> StandardValidator:
            return StandardValidator(self)

    def __init__(self, args: Args | None = None) -> None:
        self.args = args or StandardValidator.Args()
        self.parent = HubValidator(
            spawner=lambda hub: FirstMatchValidatorWorker(
                workers=(
                    AnyValidatorWorker(),
                    AnnotatedValidatorWorker(hub=hub),
                    UnionValidatorWorker(hub=hub),
                    LiteralValidatorWorker(),
                    NoneValidatorWorker(),
                    TypeInstanceValidatorWorker(datatype=bool),
                    TypeInstanceValidatorWorker(datatype=int),
                    TypeInstanceValidatorWorker(datatype=float),
                    TypeInstanceValidatorWorker(datatype=str),
                    TypeInstanceValidatorWorker(datatype=Path),
                    ListValidatorWorker(hub=hub),
                    DictValidatorWorker(hub=hub),
                    TupleValidatorWorker(hub=hub),
                    DataclassValidatorWorker(hub=hub),
                )
            )
        )

    def __call__(self, *, value: Any, dtype: Any) -> None:
        self.parent(value=value, dtype=dtype)


__all__ = ["StandardValidator"]
