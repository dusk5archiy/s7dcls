from __future__ import annotations

from collections.abc import Mapping
from dataclasses import Field, dataclass, fields
from typing import TYPE_CHECKING, Any

from s7dcls.coercers.protocol import CoercerProtocol
from s7dcls.error_paths import ErrorBatch
from s7dcls.protocols import TransformProtocol
from s7dcls.type_hints import resolve_dataclass_type

from .protocol import DataclassKwargsResolverProtocol

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


@dataclass(kw_only=True, frozen=True)
class ScaffoldDataclassKwargsResolver(DataclassKwargsResolverProtocol):
    coercer: CoercerProtocol
    class_key_projection: TransformProtocol[str] | None = None
    extra_keys_allowed: bool = False
    collect_errors: bool = False

    def __call__(
        self,
        *,
        data: Mapping[str, Any],
        datacls: type[DataclassInstance],
    ) -> dict[str, Any]:
        resolved = resolve_dataclass_type(datacls)
        if resolved is None:
            raise TypeError(
                {
                    "dtype": str(datacls),
                    "expected_type": "dataclass",
                    "got_type": str(type(datacls)),
                }
            )
        actual_cls, type_hints = resolved

        projected_key_to_definition: dict[str, Field[Any]] = {}

        for definition in fields(actual_cls):
            if not definition.init:
                continue

            alias = definition.metadata.get("alias")
            _projected_key = alias if isinstance(alias, str) else definition.name
            if self.class_key_projection is not None:
                _projected_key = self.class_key_projection(_projected_key)

            projected_key_to_definition[_projected_key] = definition

        batch = ErrorBatch(collect=self.collect_errors)
        if not self.extra_keys_allowed:
            unknown = sorted(set(data) - set(projected_key_to_definition))
            if unknown:
                batch.add(
                    exc=ValueError({"expected_type": str(datacls), "unknown": unknown})
                )

        kwargs: dict[str, Any] = {}

        for data_key, data_value in data.items():
            _definition = projected_key_to_definition.get(data_key)
            if _definition is None:
                continue

            _dtype = type_hints.get(_definition.name, _definition.type)
            with batch.capture(segment=_definition.name):
                kwargs[_definition.name] = self.coercer(value=data_value, dtype=_dtype)

        batch.raise_if_any()
        return kwargs


__all__ = ["ScaffoldDataclassKwargsResolver"]
