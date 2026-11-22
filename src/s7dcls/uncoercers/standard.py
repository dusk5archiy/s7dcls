from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.dataclass_dehydrators.protocol import DataclassDehydratorProtocol
from s7dcls.dataclass_dehydrators.scaffold import ScaffoldDataclassDehydrator

from .mechanism import (
    DataclassUncoercer,
    DictUncoercer,
    NoneUncoercer,
    PathUncoercer,
    PrimitiveUncoercer,
    SequenceUncoercer,
)
from .models import UncoerceResult
from .protocol import StrictUncoercerProtocol, UncoercerProtocol


class StandardUncoercer(StrictUncoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_dehydrator: DataclassDehydratorProtocol | None = None

        def build(self) -> StandardUncoercer:
            return StandardUncoercer(self)

    def __init__(self, args: Args) -> None:
        dataclass_dehydrator = (
            args.dataclass_dehydrator or ScaffoldDataclassDehydrator()
        )
        self.uncoercers: tuple[UncoercerProtocol, ...] = (
            NoneUncoercer(),
            PrimitiveUncoercer(),
            PathUncoercer(),
            SequenceUncoercer(inner_uncoercer=self),
            DictUncoercer(inner_uncoercer=self),
            DataclassUncoercer(
                inner_uncoercer=self,
                dataclass_dehydrator=dataclass_dehydrator,
            ),
        )

    def __call__(self, *, value: Any) -> UncoerceResult:
        for uncoercer in self.uncoercers:
            result = uncoercer(value=value)
            if result is not None:
                return result
        raise TypeError({"value": value, "got_type": str(type(value))})


__all__ = ["StandardUncoercer"]
