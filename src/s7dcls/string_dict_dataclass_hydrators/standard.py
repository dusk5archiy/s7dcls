from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from s7dcls.coercers.protocol import CoercerProtocol
from s7dcls.coercers.standard import StandardCoercer
from s7dcls.dataclass_hydrators.protocol import DataclassHydratorProtocol
from s7dcls.dataclass_hydrators.scaffold import ScaffoldDataclassHydrator
from s7dcls.string_dict_dataclass_hydrators.protocol import (
    StringDictDataclassHydratorProtocol,
)

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class StandardStringDictDataclassHydrator(StringDictDataclassHydratorProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        dataclass_hydrator: DataclassHydratorProtocol | None = None
        coercer: CoercerProtocol | None = None
        extra_keys_allowed: bool = False

        def build(self):
            return StandardStringDictDataclassHydrator(self)

    def __init__(self, args: Args):
        self.args = args
        self.dataclass_hydrator = args.dataclass_hydrator or ScaffoldDataclassHydrator()
        self.coercer = (
            args.coercer
            or StandardCoercer.Args(
                dataclass_hydrator=self.dataclass_hydrator,
            ).build()
        )

    def __call__[T: DataclassInstance](self, *, datacls: type[T], data):
        args = self.args
        return self.dataclass_hydrator(
            datacls=datacls,
            data=data,
            coercer=self.coercer,
            extra_keys_allowed=args.extra_keys_allowed,
        )
