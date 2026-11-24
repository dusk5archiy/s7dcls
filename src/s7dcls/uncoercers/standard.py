from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.dataclass_dehydrators.protocol import DataclassDehydratorFactoryProtocol
from s7dcls.dataclass_dehydrators.scaffold import ScaffoldDataclassDehydratorFactory

from .mechanism import (
    DataclassUncoercer,
    DictUncoercer,
    NoneUncoercer,
    PathUncoercer,
    PrimitiveUncoercer,
    SequenceUncoercer,
)
from .ops import FirstMatchUncoercer
from .protocol import StrictUncoercerProtocol
from .scaffold import RecursiveUncoercer


class StandardUncoercer(StrictUncoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_dehydrator_factory: DataclassDehydratorFactoryProtocol | None = None

        def build(self) -> StandardUncoercer:
            return StandardUncoercer(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardUncoercer.Args()
        dehydrator_factory = (
            active_args.dataclass_dehydrator_factory
            or ScaffoldDataclassDehydratorFactory()
        )
        self.parent = RecursiveUncoercer(
            uncoercer_recursion=lambda inner: FirstMatchUncoercer(
                uncoercers=(
                    NoneUncoercer(),
                    PrimitiveUncoercer(),
                    PathUncoercer(),
                    SequenceUncoercer(inner_uncoercer=inner),
                    DictUncoercer(inner_uncoercer=inner),
                    DataclassUncoercer(dataclass_dehydrator=dehydrator_factory(inner)),
                )
            )
        )

    def __call__(self, *, value: Any) -> Any:
        return self.parent(value=value)


__all__ = ["StandardUncoercer"]
