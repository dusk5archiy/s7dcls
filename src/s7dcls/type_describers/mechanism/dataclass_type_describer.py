from __future__ import annotations

from contextvars import ContextVar
from dataclasses import MISSING, dataclass, fields
from typing import Any, get_args, get_origin

from s7dcls.type_hints import resolve_dataclass_type

from ..docstrings import get_cached_dataclass_docstrings
from ..models import DescribeTypeResult
from ..protocol import TypeDescriberProtocol, TypeDescriberWorkerProtocol

_ACTIVE_DATACLASSES: ContextVar[frozenset[Any]] = ContextVar(
    "s7dcls_active_dataclasses", default=frozenset()
)


def _format_type_arg(arg: Any) -> str:
    origin = get_origin(arg)
    if origin is not None:
        args = get_args(arg)
        base = getattr(origin, "__name__", str(origin))
        if args:
            return f"{base}[{', '.join(_format_type_arg(a) for a in args)}]"
        return base
    return getattr(arg, "__name__", str(arg))


def _dataclass_display_name(dtype: Any, actual_cls: type[Any]) -> str:
    args = get_args(dtype)
    if not args:
        return actual_cls.__name__
    return f"{actual_cls.__name__}[{', '.join(_format_type_arg(a) for a in args)}]"


@dataclass(kw_only=True, frozen=True)
class DataclassTypeDescriberWorker(TypeDescriberWorkerProtocol):
    hub: TypeDescriberProtocol
    include_docstrings: bool = False

    def __call__(self, *, dtype: Any) -> DescribeTypeResult | None:
        resolved = resolve_dataclass_type(dtype)
        if resolved is None:
            return None

        actual_cls, type_hints = resolved
        display_name = _dataclass_display_name(dtype, actual_cls)
        active = _ACTIVE_DATACLASSES.get()
        if dtype in active:
            return DescribeTypeResult(
                schema={"type": "dataclass_ref", "name": display_name}
            )

        token = _ACTIVE_DATACLASSES.set(active | {dtype})
        try:
            docs = (
                get_cached_dataclass_docstrings(actual_cls)
                if self.include_docstrings
                else None
            )

            field_schemas: list[dict[str, Any]] = []
            for definition in fields(actual_cls):
                if not definition.init:
                    continue
                alias = definition.metadata.get("alias")
                field_name = alias if isinstance(alias, str) else definition.name
                entry: dict[str, Any] = {
                    "name": field_name,
                    "required": definition.default is MISSING
                    and definition.default_factory is MISSING,
                    "schema": self.hub(
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
                "name": display_name,
                "fields": field_schemas,
            }
            if docs is not None and docs.class_doc is not None:
                schema["description"] = docs.class_doc

            return DescribeTypeResult(schema=schema)
        finally:
            _ACTIVE_DATACLASSES.reset(token)


__all__ = ["DataclassTypeDescriberWorker"]
