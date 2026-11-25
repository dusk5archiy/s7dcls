from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.dict_transforms.protocol import DictTransformProtocol

from .protocol import SchemaDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class DecoratedSchemaDescriber(SchemaDescriberProtocol):
    schema_describer: SchemaDescriberProtocol
    dict_transform: DictTransformProtocol

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        return dict(self.dict_transform(self.schema_describer(dtype=dtype)))


__all__ = ["DecoratedSchemaDescriber"]
