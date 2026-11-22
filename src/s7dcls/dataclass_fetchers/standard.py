from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from s7dcls.dataclass_hydrators.scaffold import ScaffoldDataclassHydrator
from s7dcls.string_dict_dataclass_hydrators.standard import (
    StandardStringDictDataclassHydrator,
)
from s7dcls.string_manipulations.string_transforms.mechanism import (
    PrefixRemover,
    UpperTransform,
)
from s7dcls.string_manipulations.string_transforms.scaffold import SequenceTransform
from s7dcls.type_emitters.protocol import DataclassEmitterProtocol, EmitterProtocol

from .scaffold import ScaffoldSourceDataclassFetcher

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class StandardDataclassFetcher[T: DataclassInstance](DataclassEmitterProtocol[T]):
    @dataclass(kw_only=True, frozen=True)
    class Args[D: DataclassInstance]:
        datacls: type[D]
        dict_emitter: EmitterProtocol[dict[str, str]]

        def build(self):
            return StandardDataclassFetcher(self)

    def __init__(self, args: Args[T]):

        self.parent = ScaffoldSourceDataclassFetcher(
            datacls=args.datacls,
            dict_emitter=args.dict_emitter,
            string_dict_dataclass_hydrator=StandardStringDictDataclassHydrator.Args(
                dataclass_hydrator=ScaffoldDataclassHydrator(
                    class_key_projection=SequenceTransform(
                        transforms=[
                            PrefixRemover(prefix="_"),
                            UpperTransform(),
                        ]
                    ),
                    data_key_projection=UpperTransform(),
                ),
                extra_keys_allowed=True,
            ).build(),
        )

    def __call__(self):
        return self.parent()
