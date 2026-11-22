from __future__ import annotations

from dataclasses import dataclass

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerProtocol


@dataclass(kw_only=True, frozen=True)
class StringBoolCoercer(CoercerProtocol):
    trues: tuple[str, ...] = ("1", "true", "yes", "on")
    falses: tuple[str, ...] = ("0", "false", "no", "off")

    def __call__(self, *, value, dtype):
        if dtype is not bool:
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
        if s in self.trues:
            return CoerceResult(value=True)
        if s in self.falses:
            return CoerceResult(value=False)

        raise ValueError({"value": value, "expected_type": str(dtype)})


__all__ = ["StringBoolCoercer"]
