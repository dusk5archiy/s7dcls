from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mechanism import (
    AnnotatedValidator,
    AnyValidator,
    DataclassValidator,
    DictValidator,
    ListValidator,
    LiteralValidator,
    NoneValidator,
    TupleValidator,
    TypeInstanceValidator,
    UnionValidator,
)
from .ops import FirstMatchValidator
from .protocol import StrictValidatorProtocol
from .scaffold import RecursiveValidator


class StandardValidator(StrictValidatorProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        def build(self) -> StandardValidator:
            return StandardValidator(self)

    def __init__(self, args: Args | None = None) -> None:
        self.args = args or StandardValidator.Args()
        self.parent = RecursiveValidator(
            validator_recursion=lambda inner: FirstMatchValidator(
                validators=(
                    AnyValidator(),
                    AnnotatedValidator(inner_validator=inner),
                    UnionValidator(inner_validator=inner),
                    LiteralValidator(),
                    NoneValidator(),
                    TypeInstanceValidator(datatype=bool),
                    TypeInstanceValidator(datatype=int),
                    TypeInstanceValidator(datatype=float),
                    TypeInstanceValidator(datatype=str),
                    TypeInstanceValidator(datatype=Path),
                    ListValidator(inner_validator=inner),
                    DictValidator(inner_validator=inner),
                    TupleValidator(inner_validator=inner),
                    DataclassValidator(inner_validator=inner),
                )
            )
        )

    def __call__(self, *, value: Any, dtype: Any) -> None:
        self.parent(value=value, dtype=dtype)


__all__ = ["StandardValidator"]
