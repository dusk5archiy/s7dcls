from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerProtocol


@dataclass(kw_only=True, frozen=True)
class PathUncoercer(UncoercerProtocol):
    def __call__(self, *, value):
        if isinstance(value, Path):
            return UncoerceResult(value=str(value))
        return None


__all__ = ["PathUncoercer"]
