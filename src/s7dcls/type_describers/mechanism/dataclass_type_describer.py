from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from s7dcls.type_hints import get_cached_type_hints

from ..models import DescribeTypeResult
from ..protocol import StrictTypeDescriberProtocol, TypeDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class DataclassTypeDescriber(TypeDescriberProtocol):
    inner_type_describer: StrictTypeDescriberProtocol

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if not isinstance(dtype, type) or not is_dataclass(dtype):
            return None

        type_hints = get_cached_type_hints(dtype)
        field_schemas = [
            {
                "name": definition.name,
                "schema": self.inner_type_describer(
                    dtype=type_hints.get(definition.name, definition.type)
                ),
            }
            for definition in fields(dtype)
            if definition.init
        ]
        return DescribeTypeResult(
            schema={
                "type": "dataclass",
                "name": dtype.__name__,
                "fields": field_schemas,
            }
        )


__all__ = ["DataclassTypeDescriber"]
