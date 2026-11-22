from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from s7dcls.type_emitters.protocol import TransformProtocol

from .protocol import DataclassDehydratorProtocol


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassDehydrator(DataclassDehydratorProtocol):
    class_key_projection: TransformProtocol[str] | None = None
    include_non_init: bool = False

    def __call__(self, *, instance, uncoercer):
        if not is_dataclass(instance) or isinstance(instance, type):
            raise TypeError({"value": instance, "expected": "dataclass instance"})

        result: dict[str, Any] = {}
        for definition in fields(instance):
            if not self.include_non_init and not definition.init:
                continue

            key = definition.name
            if self.class_key_projection is not None:
                key = self.class_key_projection(key)

            raw_value = getattr(instance, definition.name)
            result[key] = uncoercer(value=raw_value).value

        return result


__all__ = ["ScaffoldDataclassDehydrator"]
