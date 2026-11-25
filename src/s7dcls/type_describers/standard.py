from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mechanism import (
    AnnotatedTypeDescriberWorker,
    AnyTypeDescriberWorker,
    DataclassTypeDescriberWorker,
    DictTypeDescriberWorker,
    ListTypeDescriberWorker,
    LiteralTypeDescriberWorker,
    NoneTypeDescriberWorker,
    TupleTypeDescriberWorker,
    TypeInstanceDescriberWorker,
    UnionTypeDescriberWorker,
)
from .ops import FirstMatchTypeDescriberWorker
from .protocol import TypeDescriberProtocol
from .scaffold import HubTypeDescriber


class StandardTypeDescriber(TypeDescriberProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        include_docstrings: bool = False

        def build(self) -> StandardTypeDescriber:
            return StandardTypeDescriber(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardTypeDescriber.Args()
        self.parent = HubTypeDescriber(
            spawner=lambda hub: FirstMatchTypeDescriberWorker(
                workers=(
                    AnyTypeDescriberWorker(),
                    AnnotatedTypeDescriberWorker(hub=hub),
                    UnionTypeDescriberWorker(hub=hub),
                    LiteralTypeDescriberWorker(),
                    NoneTypeDescriberWorker(),
                    TypeInstanceDescriberWorker(datatype=bool, type_name="bool"),
                    TypeInstanceDescriberWorker(datatype=int, type_name="int"),
                    TypeInstanceDescriberWorker(datatype=float, type_name="float"),
                    TypeInstanceDescriberWorker(datatype=str, type_name="str"),
                    TypeInstanceDescriberWorker(datatype=Path, type_name="path"),
                    ListTypeDescriberWorker(hub=hub),
                    TupleTypeDescriberWorker(hub=hub),
                    DictTypeDescriberWorker(hub=hub),
                    DataclassTypeDescriberWorker(
                        hub=hub,
                        include_docstrings=active_args.include_docstrings,
                    ),
                )
            )
        )

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        return self.parent(dtype=dtype)


__all__ = ["StandardTypeDescriber"]
