from __future__ import annotations

from dataclasses import dataclass

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import StrictUncoercerProtocol, UncoercerProtocol


@dataclass(kw_only=True, frozen=True)
class SequenceUncoercer(UncoercerProtocol):
    inner_uncoercer: StrictUncoercerProtocol

    def __call__(self, *, value):
        if not isinstance(value, (list, tuple)):
            return None
        return UncoerceResult(
            value=[self.inner_uncoercer(value=item) for item in value]
        )


__all__ = ["SequenceUncoercer"]
