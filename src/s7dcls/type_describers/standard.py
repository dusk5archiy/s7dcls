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
from .ops import FirstMatchTypeDescriber
from .protocol import StrictTypeDescriberProtocol
from .scaffold import RecursiveTypeDescriber


class StandardTypeDescriber(StrictTypeDescriberProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        include_docstrings: bool = False

        def build(self) -> StandardTypeDescriber:
            return StandardTypeDescriber(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardTypeDescriber.Args()
        self.parent = RecursiveTypeDescriber(
            describer_recursion=lambda inner: FirstMatchTypeDescriber(
                describers=(
                    AnyTypeDescriber(),
                    AnnotatedTypeDescriber(inner_type_describer=inner),
                    UnionTypeDescriber(inner_type_describer=inner),
                    LiteralTypeDescriber(),
                    NoneTypeDescriber(),
                    TypeInstanceDescriber(datatype=bool, type_name="bool"),
                    TypeInstanceDescriber(datatype=int, type_name="int"),
                    TypeInstanceDescriber(datatype=float, type_name="float"),
                    TypeInstanceDescriber(datatype=str, type_name="str"),
                    TypeInstanceDescriber(datatype=Path, type_name="path"),
                    ListTypeDescriber(inner_type_describer=inner),
                    TupleTypeDescriber(inner_type_describer=inner),
                    DictTypeDescriber(inner_type_describer=inner),
                    DataclassTypeDescriber(
                        inner_type_describer=inner,
                        include_docstrings=active_args.include_docstrings,
                    ),
                )
            )
        )

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        return self.parent(dtype=dtype)


__all__ = ["StandardTypeDescriber"]
