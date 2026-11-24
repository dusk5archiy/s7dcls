from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .models import CoerceResult
from .protocol import CoercerProtocol, StrictCoercerProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchCoercer(CoercerProtocol):
    coercers: Sequence[CoercerProtocol]

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Any] | None:
        for coercer in self.coercers:
            result = coercer(value=value, dtype=dtype)
            if result is not None:
                return result
        return None


@dataclass(kw_only=True, frozen=True)
class FallbackCoercer(StrictCoercerProtocol):
    coercers: Sequence[StrictCoercerProtocol]

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        errors: list[Exception] = []
        for coercer in self.coercers:
            try:
                return coercer(value=value, dtype=dtype)
            except (TypeError, ValueError) as e:
                errors.append(e)

        if errors:
            if any(isinstance(e, ValueError) for e in errors):
                raise ValueError(
                    {"value": value, "expected_type": str(dtype), "errors": errors}
                ) from errors[-1]
            raise TypeError(
                {"value": value, "expected_type": str(dtype), "errors": errors}
            ) from errors[-1]

        raise TypeError({"value": value, "expected_type": str(dtype)})


__all__ = ["FallbackCoercer", "FirstMatchCoercer"]
