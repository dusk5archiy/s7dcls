from __future__ import annotations

from dataclasses import dataclass

from s7dcls.protocols import TransformProtocol

from .protocol import StringGateProtocol


@dataclass(kw_only=True, frozen=True)
class DecoratedStringGate(StringGateProtocol):
    string_gate: StringGateProtocol
    string_transform: TransformProtocol[str]

    def __call__(self, x: str, /) -> str | None:
        out = self.string_gate(x)
        if out is None:
            return None
        return self.string_transform(out)


__all__ = ["DecoratedStringGate"]
