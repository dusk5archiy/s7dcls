from __future__ import annotations

from collections.abc import Mapping
from dataclasses import Field, dataclass, fields
from typing import TYPE_CHECKING, Any

from s7dcls.coercers.protocol import StrictCoercerProtocol
from s7dcls.type_emitters.protocol import TransformProtocol
from s7dcls.type_hints import get_cached_type_hints

from .protocol import DataclassKwargsResolverProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassKwargsResolver(DataclassKwargsResolverProtocol):
    coercer: StrictCoercerProtocol
    class_key_projection: TransformProtocol[str] | None = None
    data_key_projection: TransformProtocol[str] | None = None
    extra_keys_allowed: bool = False

    def __call__(
        self,
        *,
        data: Mapping[str, Any],
        datacls: type[DataclassInstance],
    ) -> dict[str, Any]:
        projected_key_to_definition: dict[str, Field[Any]] = {}

        for definition in fields(datacls):
            if not definition.init:
                continue

            _projected_key = definition.name
            if self.class_key_projection is not None:
                _projected_key = self.class_key_projection(_projected_key)

            projected_key_to_definition[_projected_key] = definition

        projected_key_to_data_value: dict[str, Any] = {}
        for data_key, data_value in data.items():
            _projected_key = data_key
            if self.data_key_projection is not None:
                _projected_key = self.data_key_projection(data_key)

            projected_key_to_data_value[_projected_key] = data_value

        if not self.extra_keys_allowed:
            unknown = sorted(
                set(projected_key_to_data_value) - set(projected_key_to_definition)
            )
            if unknown:
                raise ValueError({"expected_type": str(datacls), "unknown": unknown})

        type_hints = get_cached_type_hints(datacls)
        kwargs: dict[str, Any] = {}

        for projected_key, data_value in projected_key_to_data_value.items():
            _definition = projected_key_to_definition.get(projected_key)
            if _definition is None:
                continue

            _dtype = type_hints.get(_definition.name, _definition.type)
            kwargs[_definition.name] = self.coercer(value=data_value, dtype=_dtype)

        return kwargs


__all__ = ["ScaffoldDataclassKwargsResolver"]
