from __future__ import annotations

from typing import Any

from .protocol import UncoercerProtocol, UncoercerSpawnerProtocol


class HubUncoercer(UncoercerProtocol):
    def __init__(self, *, spawner: UncoercerSpawnerProtocol) -> None:
        self.worker = spawner(self)

    def __call__(self, *, value: Any) -> Any:
        result = self.worker(value=value)
        if result is not None:
            return result.value
        raise TypeError({"value": value, "got_type": str(type(value))})


__all__ = ["HubUncoercer"]
