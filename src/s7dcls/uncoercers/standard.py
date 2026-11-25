from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.dataclass_dehydrators.protocol import DataclassDehydratorFactoryProtocol
from s7dcls.dataclass_dehydrators.scaffold import ScaffoldDataclassDehydratorFactory

from .mechanism import (
    DataclassUncoercerWorker,
    DictUncoercerWorker,
    NoneUncoercerWorker,
    PathUncoercerWorker,
    PrimitiveUncoercerWorker,
    SequenceUncoercerWorker,
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
            or ScaffoldDataclassDehydratorFactory()
        )
        self.parent = HubUncoercer(
            spawner=lambda hub: FirstMatchUncoercerWorker(
                workers=(
                    NoneUncoercerWorker(),
                    PrimitiveUncoercerWorker(),
                    PathUncoercerWorker(),
                    SequenceUncoercerWorker(hub=hub),
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
