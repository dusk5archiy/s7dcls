from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import TYPE_CHECKING, Any

from s7dcls.type_emitters.protocol import TransformProtocol

from .protocol import DataclassDehydratorFactoryProtocol, DataclassDehydratorProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    from s7dcls.uncoercers.protocol import StrictUncoercerProtocol


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassDehydrator(DataclassDehydratorProtocol):
    uncoercer: StrictUncoercerProtocol
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

            key = definition.name
            if self.class_key_projection is not None:
                key = self.class_key_projection(key)

            raw_value = getattr(instance, definition.name)
            result[key] = self.uncoercer(value=raw_value)

        return result


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassDehydratorFactory(DataclassDehydratorFactoryProtocol):
    class_key_projection: TransformProtocol[str] | None = None
    include_non_init: bool = False

    def __call__(
        self, uncoercer: StrictUncoercerProtocol
    ) -> DataclassDehydratorProtocol:
        return ScaffoldDataclassDehydrator(
            uncoercer=uncoercer,
            class_key_projection=self.class_key_projection,
            include_non_init=self.include_non_init,
        )


__all__ = ["ScaffoldDataclassDehydrator", "ScaffoldDataclassDehydratorFactory"]
