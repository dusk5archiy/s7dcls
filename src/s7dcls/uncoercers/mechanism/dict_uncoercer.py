from __future__ import annotations

from dataclasses import dataclass

from s7dcls.uncoercers.models import UncoerceResult
from s7dcls.uncoercers.protocol import UncoercerProtocol, UncoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class DictUncoercerWorker(UncoercerWorkerProtocol):
    hub: UncoercerProtocol

    def __call__(self, *, value):
        if not isinstance(value, dict):
            return None
        result = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise TypeError(
                    {
                        "key": k,
                        "expected_type": str(str),
                        "got_type": str(type(k)),
                    }
                )
            result[k] = self.hub(value=v)
        return UncoerceResult(value=result)


__all__ = ["DictUncoercerWorker"]
