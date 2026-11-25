from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.type_describers.standard import StandardTypeDescriber

from .mechanism import JsonSchemaDictTransform
from .protocol import SchemaDescriberProtocol
from .scaffold import ChainSchemaDescriber


class StandardJsonSchemaDescriber(SchemaDescriberProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        include_docstrings: bool = False

        def build(self) -> StandardJsonSchemaDescriber:
            return StandardJsonSchemaDescriber(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardJsonSchemaDescriber.Args()
        self.parent = ChainSchemaDescriber(
            type_describer=StandardTypeDescriber.Args(
                include_docstrings=active_args.include_docstrings
            ).build(),
            dict_transform=JsonSchemaDictTransform(),
        )

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        return self.parent(dtype=dtype)


__all__ = ["StandardJsonSchemaDescriber"]
