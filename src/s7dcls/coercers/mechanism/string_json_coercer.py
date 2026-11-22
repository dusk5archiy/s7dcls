from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from s7dcls.coercers.protocol import CoercerProtocol, StrictJsonCoercerProtocol


@dataclass(kw_only=True, frozen=True)
class StringJsonCoercer(CoercerProtocol):
    json_coercer: StrictJsonCoercerProtocol

    def can_handle(self, *, dtype: Any) -> bool:
        return self.json_coercer.can_handle(dtype=dtype)

    def __call__(self, *, value, dtype):
        if not self.can_handle(dtype=dtype):
            return None

        if not isinstance(value, str):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(str),
                    "got_type": str(type(value)),
                }
            )

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(
                {"value": value, "expected_type": str(dtype), "e": e}
            ) from e

        return self.json_coercer(value=parsed, dtype=dtype)


__all__ = ["StringJsonCoercer"]
