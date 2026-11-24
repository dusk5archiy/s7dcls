from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class CoerceResult[T]:
    value: T


__all__ = ["CoerceResult"]
