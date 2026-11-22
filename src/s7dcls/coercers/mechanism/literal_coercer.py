from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, get_args, get_origin

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, StrictCoercerProtocol


@dataclass(kw_only=True, frozen=True)
class LiteralCoercer(CoercerProtocol):
    inner_coercer: StrictCoercerProtocol | None = None

    def __call__(self, *, value, dtype):
        if get_origin(dtype) is not Literal:
            return None

        allowed = get_args(dtype)
        for choice in allowed:
            if self.inner_coercer is not None:
                try:
                    coerced = self.inner_coercer(value=value, dtype=type(choice))
                except (ValueError, TypeError):
                    continue
                if coerced == choice and type(coerced) is type(choice):
                    return CoerceResult(value=choice)
            elif value == choice and type(value) is type(choice):
                return CoerceResult(value=choice)

        raise ValueError({"value": value, "expected_type": str(dtype)})


__all__ = ["LiteralCoercer"]
