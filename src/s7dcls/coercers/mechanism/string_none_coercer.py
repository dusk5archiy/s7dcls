from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol


@dataclass(kw_only=True, frozen=True)
class StringNoneCoercer(CoercerProtocol):
    values: Sequence[str] = ("", "none", "null")

    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[None] | None:
        if dtype is not type(None) and dtype is not None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                {
                    "value": value,
                    "expected_type": str(str),
                    "got_type": str(type(value)),
                }
            )

        s = value.strip().lower()
        if s in self.values:
            return CoerceResult(value=None)

        raise ValueError({"value": value, "expected_type": str(dtype)})


__all__ = ["StringNoneCoercer"]
