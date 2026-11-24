from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class ValidateResult:
    pass


__all__ = ["ValidateResult"]
