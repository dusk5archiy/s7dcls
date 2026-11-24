from __future__ import annotations

from s7dcls.type_emitters.protocol import FunctionProtocol

StringGateProtocol = FunctionProtocol[str, str | None]


__all__ = ["StringGateProtocol"]
