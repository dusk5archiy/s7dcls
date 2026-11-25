from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from .mechanism import (
    AnnotatedTypeDescriberWorker,
    AnyTypeDescriberWorker,
    DataclassTypeDescriberWorker,
    DictTypeDescriberWorker,
    EnumTypeDescriberWorker,
    ListTypeDescriberWorker,
    LiteralTypeDescriberWorker,
    NoneTypeDescriberWorker,
    SetTypeDescriberWorker,
    TupleTypeDescriberWorker,
    TypeAliasTypeDescriberWorker,
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
                    TypeAliasTypeDescriberWorker(hub=hub),
                    AnyTypeDescriberWorker(),
                    AnnotatedTypeDescriberWorker(hub=hub),
                    UnionTypeDescriberWorker(hub=hub),
                    LiteralTypeDescriberWorker(),
                    NoneTypeDescriberWorker(),
                    EnumTypeDescriberWorker(),
                    TypeInstanceDescriberWorker(datatype=bool, type_name="bool"),
                    TypeInstanceDescriberWorker(datatype=int, type_name="int"),
                    TypeInstanceDescriberWorker(datatype=float, type_name="float"),
                    TypeInstanceDescriberWorker(datatype=str, type_name="str"),
                    TypeInstanceDescriberWorker(datatype=Path, type_name="path"),
                    TypeInstanceDescriberWorker(datatype=UUID, type_name="uuid"),
                    TypeInstanceDescriberWorker(
                        datatype=datetime, type_name="datetime"
                    ),
                    TypeInstanceDescriberWorker(datatype=date, type_name="date"),
                    TypeInstanceDescriberWorker(
                        datatype=timedelta, type_name="timedelta"
                    ),
                    TypeInstanceDescriberWorker(datatype=Decimal, type_name="decimal"),
                    ListTypeDescriberWorker(hub=hub),
                    SetTypeDescriberWorker(hub=hub),
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
