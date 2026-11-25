from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .protocol import UncoercerProtocol, UncoercerSpawnerProtocol


class HubUncoercer(UncoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        spawner: UncoercerSpawnerProtocol

        def build(self) -> HubUncoercer:
            return HubUncoercer(self)

    def __init__(self, args: Args) -> None:
        self.worker = args.spawner(self)

    def __call__(self, *, value: Any) -> Any:
        result = self.worker(value=value)
        if result is not None:
            return result.value
        raise TypeError({"value": value, "got_type": str(type(value))})


__all__ = ["HubUncoercer"]
