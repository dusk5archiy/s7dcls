from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from s7dcls.protocols import TransformProtocol

from ..protocol import DataclassDehydratorFactoryProtocol, DataclassDehydratorProtocol
from ..scaffold import ScaffoldDataclassDehydrator

if TYPE_CHECKING:
    from s7dcls.uncoercers.protocol import UncoercerProtocol


class StandardDataclassDehydratorFactory(DataclassDehydratorFactoryProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        class_key_projection: TransformProtocol[str] | None = None
        include_non_init: bool = False

        def build(self) -> StandardDataclassDehydratorFactory:
            return StandardDataclassDehydratorFactory(self)

    def __init__(self, args: Args | None = None) -> None:
        self.args = args or StandardDataclassDehydratorFactory.Args()

    def __call__(self, uncoercer: UncoercerProtocol) -> DataclassDehydratorProtocol:
        return ScaffoldDataclassDehydrator(
            uncoercer=uncoercer,
            class_key_projection=self.args.class_key_projection,
            include_non_init=self.args.include_non_init,
        )


__all__ = ["StandardDataclassDehydratorFactory"]
