from __future__ import annotations

from dataclasses import dataclass

from .protocol import StringGateProtocol


@dataclass(kw_only=True, frozen=True)
class PrefixGate(StringGateProtocol):
    prefix: str

    def __call__(self, string: str) -> str | None:
        if string.startswith(self.prefix):
            return string[len(self.prefix) :]

        return None


@dataclass(kw_only=True, frozen=True)
class NoCasePrefixGate(StringGateProtocol):
    prefix: str

    def __call__(self, string: str) -> str | None:
        _normalized_string = string.upper()
        _normalized_prefix = self.prefix.upper()
        if _normalized_string.startswith(_normalized_prefix):
            return string[len(self.prefix) :]

        return None


__all__ = ["NoCasePrefixGate", "PrefixGate"]
