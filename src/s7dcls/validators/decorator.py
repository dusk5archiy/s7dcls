from __future__ import annotations

from dataclasses import fields, is_dataclass
from functools import wraps
from typing import Any

from s7dcls.error_paths import ErrorBatch
from s7dcls.type_hints import get_cached_type_hints

from .protocol import ValidatorProtocol
from .standard import StandardValidator


def validate[T](
    cls: type[T],
    *,
    validator: ValidatorProtocol | None = None,
    collect_errors: bool = False,
) -> type[T]:
    """Dataclass decorator that validates init fields after __init__."""
    if not is_dataclass(cls):
        raise TypeError({"dtype": str(cls), "expected_type": "dataclass"})

    active_validator = (
        validator or StandardValidator.Args(collect_errors=collect_errors).build()
    )
    type_hints = get_cached_type_hints(cls)
    field_specs = tuple(
        (definition.name, type_hints.get(definition.name, definition.type))
        for definition in fields(cls)
        if definition.init
    )

    orig_init = cls.__init__

    @wraps(orig_init)
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None:
        orig_init(self, *args, **kwargs)
        batch = ErrorBatch(collect=collect_errors)
        for field_name, field_dtype in field_specs:
            field_value = getattr(self, field_name)
            with batch.capture(segment=field_name):
                active_validator(value=field_value, dtype=field_dtype)
        batch.raise_if_any()

    cls.__init__ = __init__  # type: ignore[method-assign]
    return cls


__all__ = ["validate"]
