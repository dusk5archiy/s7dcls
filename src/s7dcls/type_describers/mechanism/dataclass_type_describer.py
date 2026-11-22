from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from s7dcls.type_hints import get_cached_type_hints

from ..docstrings import get_cached_dataclass_docstrings
from ..models import DescribeTypeResult
from ..protocol import StrictTypeDescriberProtocol, TypeDescriberProtocol


@dataclass(kw_only=True, frozen=True)
class DataclassTypeDescriber(TypeDescriberProtocol):
    inner_type_describer: StrictTypeDescriberProtocol
    include_docstrings: bool = False

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        if not isinstance(dtype, type) or not is_dataclass(dtype):
            return None

        type_hints = get_cached_type_hints(dtype)
        docs = (
            get_cached_dataclass_docstrings(dtype) if self.include_docstrings else None
        )

        field_schemas: list[dict[str, Any]] = []
        for definition in fields(dtype):
            if not definition.init:
                continue
            entry: dict[str, Any] = {
                "name": definition.name,
                "schema": self.inner_type_describer(
                    dtype=type_hints.get(definition.name, definition.type)
                ),
            }
            if docs is not None:
                field_doc = docs.field_docs.get(definition.name)
                if field_doc is not None:
                    entry["description"] = field_doc
            field_schemas.append(entry)

        schema: dict[str, Any] = {
            "type": "dataclass",
            "name": dtype.__name__,
            "fields": field_schemas,
        }
        if docs is not None and docs.class_doc is not None:
            schema["description"] = docs.class_doc

        return DescribeTypeResult(schema=schema)


__all__ = ["DataclassTypeDescriber"]
