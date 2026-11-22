from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, get_args, get_origin

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol, StrictCoercerProtocol
from s7dcls.value_checkers.protocol import ValueCheckerProtocol


@dataclass(kw_only=True, frozen=True)
class AnnotatedCoercer(CoercerProtocol):
    inner_coercer: StrictCoercerProtocol

    def __call__(self, *, value, dtype):
        if get_origin(dtype) is not Annotated:
            return None

        base_type, *extras = get_args(dtype)
        coerced = self.inner_coercer(value=value, dtype=base_type)

        for extra in extras:
            if isinstance(extra, ValueCheckerProtocol):
                extra(coerced)

        return CoerceResult(value=coerced)


__all__ = ["AnnotatedCoercer"]
