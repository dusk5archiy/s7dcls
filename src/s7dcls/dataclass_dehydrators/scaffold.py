from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import TYPE_CHECKING, Any

from s7dcls.error_paths import ErrorPath
from s7dcls.protocols import TransformProtocol

from .protocol import DataclassDehydratorProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from s7dcls.uncoercers.protocol import UncoercerProtocol


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassDehydrator(DataclassDehydratorProtocol):
    uncoercer: UncoercerProtocol
    class_key_projection: TransformProtocol[str] | None = None
    include_non_init: bool = False

    def __call__(self, *, instance: DataclassInstance) -> dict[str, Any]:
        if not is_dataclass(instance) or isinstance(instance, type):
            raise TypeError(
                {
                    "value": instance,
                    "expected_type": "dataclass",
                    "got_type": str(type(instance)),
                }
            )

        result: dict[str, Any] = {}
        for definition in fields(instance):
            if not self.include_non_init and not definition.init:
                continue

            alias = definition.metadata.get("alias")
            key = alias if isinstance(alias, str) else definition.name
            if self.class_key_projection is not None:
                key = self.class_key_projection(key)

            raw_value = getattr(instance, definition.name)
            with ErrorPath(segment=definition.name):
                result[key] = self.uncoercer(value=raw_value)

        return result


__all__ = ["ScaffoldDataclassDehydrator"]
