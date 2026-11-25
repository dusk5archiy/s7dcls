from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.dataclass_dehydrators.protocol import DataclassDehydratorFactoryProtocol
from s7dcls.dataclass_dehydrators.standard.factory import (
    StandardDataclassDehydratorFactory,
)

from .mechanism import (
    DataclassUncoercerWorker,
    DateTimeUncoercerWorker,
    DecimalUncoercerWorker,
    DictUncoercerWorker,
    EnumUncoercerWorker,
    NoneUncoercerWorker,
    PathUncoercerWorker,
    PrimitiveUncoercerWorker,
    SequenceUncoercerWorker,
    SetUncoercerWorker,
    UuidUncoercerWorker,
)
from .ops import FirstMatchUncoercerWorker
from .protocol import UncoercerProtocol
from .scaffold import HubUncoercer


class StandardUncoercer(UncoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_dehydrator_factory: DataclassDehydratorFactoryProtocol | None = None

        def build(self) -> StandardUncoercer:
            return StandardUncoercer(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardUncoercer.Args()
        dehydrator_factory = (
            active_args.dataclass_dehydrator_factory
            or StandardDataclassDehydratorFactory.Args().build()
        )
        self.parent = HubUncoercer(
            spawner=lambda hub: FirstMatchUncoercerWorker(
                workers=(
                    NoneUncoercerWorker(),
                    EnumUncoercerWorker(hub=hub),
                    PrimitiveUncoercerWorker(),
                    PathUncoercerWorker(),
                    UuidUncoercerWorker(),
                    DateTimeUncoercerWorker(),
                    DecimalUncoercerWorker(),
                    SequenceUncoercerWorker(hub=hub),
                    SetUncoercerWorker(hub=hub),
                    DictUncoercerWorker(hub=hub),
                    DataclassUncoercerWorker(
                        dataclass_dehydrator=dehydrator_factory(hub)
                    ),
                )
            )
        )

    def __call__(self, *, value: Any) -> Any:
        return self.parent(value=value)


__all__ = ["StandardUncoercer"]
