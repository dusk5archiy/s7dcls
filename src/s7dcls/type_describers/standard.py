from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mechanism import (
    AnnotatedTypeDescriber,
    AnyTypeDescriber,
    DataclassTypeDescriber,
    DictTypeDescriber,
    ListTypeDescriber,
    LiteralTypeDescriber,
    NoneTypeDescriber,
    TupleTypeDescriber,
    TypeInstanceDescriber,
    UnionTypeDescriber,
)
from .protocol import StrictTypeDescriberProtocol, TypeDescriberProtocol


class StandardTypeDescriber(StrictTypeDescriberProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        include_docstrings: bool = False

        def build(self) -> StandardTypeDescriber:
            return StandardTypeDescriber(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardTypeDescriber.Args()
        self.describers: tuple[TypeDescriberProtocol, ...] = (
            AnyTypeDescriber(),
            AnnotatedTypeDescriber(inner_type_describer=self),
            UnionTypeDescriber(inner_type_describer=self),
            LiteralTypeDescriber(),
            NoneTypeDescriber(),
            TypeInstanceDescriber(datatype=bool, type_name="bool"),
            TypeInstanceDescriber(datatype=int, type_name="int"),
            TypeInstanceDescriber(datatype=float, type_name="float"),
            TypeInstanceDescriber(datatype=str, type_name="str"),
            TypeInstanceDescriber(datatype=Path, type_name="path"),
            ListTypeDescriber(inner_type_describer=self),
            TupleTypeDescriber(inner_type_describer=self),
            DictTypeDescriber(inner_type_describer=self),
            DataclassTypeDescriber(
                inner_type_describer=self,
                include_docstrings=active_args.include_docstrings,
            ),
        )

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        for describer in self.describers:
            result = describer(dtype=dtype)
            if result is not None:
                return result.schema
        raise TypeError({"dtype": str(dtype)})


__all__ = ["StandardTypeDescriber"]
