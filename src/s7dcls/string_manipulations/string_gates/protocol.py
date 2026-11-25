from __future__ import annotations

from s7dcls.protocols import FunctionProtocol

StringGateProtocol = FunctionProtocol[str, str | None]


__all__ = ["StringGateProtocol"]
