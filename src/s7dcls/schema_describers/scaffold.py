from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from s7dcls.dict_transforms.protocol import DictTransformProtocol
from s7dcls.type_describers.protocol import TypeDescriberProtocol

from .protocol import SchemaDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class ChainSchemaDescriber(SchemaDescriberProtocol):
    type_describer: TypeDescriberProtocol
    dict_transform: DictTransformProtocol

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        return dict(self.dict_transform(self.type_describer(dtype=dtype)))


__all__ = ["ChainSchemaDescriber"]
