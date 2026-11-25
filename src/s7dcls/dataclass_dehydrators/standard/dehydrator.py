from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..protocol import DataclassDehydratorProtocol
from ..scaffold import ScaffoldDataclassDehydrator

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from s7dcls.uncoercers.protocol import UncoercerProtocol


class StandardDataclassDehydrator(DataclassDehydratorProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        uncoercer: UncoercerProtocol | None = None

        def build(self) -> StandardDataclassDehydrator:
            return StandardDataclassDehydrator(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardDataclassDehydrator.Args()
        uncoercer = active_args.uncoercer
        if uncoercer is None:
            from s7dcls.uncoercers.standard import StandardUncoercer

            uncoercer = StandardUncoercer.Args().build()

        self.parent = ScaffoldDataclassDehydrator(uncoercer=uncoercer)

    def __call__(self, *, instance: DataclassInstance) -> dict[str, Any]:
        return self.parent(instance=instance)


__all__ = ["StandardDataclassDehydrator"]
