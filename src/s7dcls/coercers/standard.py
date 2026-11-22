from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import (
    CoercerProtocol,
    JsonCoercerProtocol,
    StrictCoercerProtocol,
    StrictJsonCoercerProtocol,
)
from s7dcls.dataclass_hydrators.protocol import DataclassHydratorProtocol
from s7dcls.dataclass_hydrators.scaffold import ScaffoldDataclassHydrator
from s7dcls.validators.mechanism import LiteralValidator

from .mechanism import (
    AnnotatedCoercer,
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


def _to_coercer_string(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


CoercerMode = Literal["json", "string"]


class StandardCoercer(StrictJsonCoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        mode: CoercerMode = "string"
        dataclass_hydrator: DataclassHydratorProtocol | None = None
        string_fallback: StrictCoercerProtocol | None = None

        def __post_init__(self) -> None:
            LiteralValidator()(value=self.mode, dtype=CoercerMode)

        def build(self) -> StandardCoercer:
            return StandardCoercer(self)

    def __init__(self, args: Args) -> None:
        self.args = args
        dataclass_hydrator = args.dataclass_hydrator or ScaffoldDataclassHydrator()
        self.container_coercers: list[JsonCoercerProtocol] = []
        self.coercers: list[CoercerProtocol] = []
        if args.mode == "json":
            self.container_coercers.extend(
                (
                    DictCoercer(inner_coercer=self),
                    ListCoercer(inner_coercer=self),
                    TupleCoercer(inner_coercer=self),
                    DataclassCoercer(
                        inner_coercer=self,
                        dataclass_hydrator=dataclass_hydrator,
                    ),
                )
            )
            self.coercers.extend(
                (
                    AnnotatedCoercer(inner_coercer=self),
                    UnionCoercer(inner_coercer=self),
                    LiteralCoercer(inner_coercer=self),
                    *self.container_coercers,
                    NoneCoercer(),
                    TypeInstanceCoercer(datatype=bool),
                    TypeInstanceCoercer(datatype=int),
                    TypeInstanceCoercer(datatype=float),
                    TypeInstanceCoercer(datatype=str),
                    PathCoercer(),
                )
            )
        elif args.mode == "string":
            json_coercer = StandardCoercer.Args(
                mode="json",
                dataclass_hydrator=dataclass_hydrator,
                string_fallback=self,
            ).build()
            self.coercers.extend(
                (
                    AnnotatedCoercer(inner_coercer=self),
                    UnionCoercer(inner_coercer=self),
                    LiteralCoercer(inner_coercer=self),
                    StringBoolCoercer(),
                    StringTypeCallCoercer(datatype=int),
                    StringTypeCallCoercer(datatype=float),
                    StringTypeCallCoercer(datatype=Path),
                    StringJsonCoercer(json_coercer=json_coercer),
                    StringTypeCallCoercer(datatype=str),
                    StringNoneCoercer(),
                )
            )

    def can_handle(self, *, dtype: Any) -> bool:
        return any(
            coercer.can_handle(dtype=dtype) for coercer in self.container_coercers
        )

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult:
        args = self.args
        if args.mode == "json" and dtype is Any:
            return CoerceResult(value=value)

        for coercer in self.coercers:
            _result = coercer(value=value, dtype=dtype)
            if _result is not None:
                return _result

        if args.mode == "json" and args.string_fallback is not None:
            return args.string_fallback(
                value=_to_coercer_string(value),
                dtype=dtype,
            )

        raise TypeError({"value": value, "expected_type": str(dtype)})


__all__ = ["CoercerMode", "StandardCoercer"]
