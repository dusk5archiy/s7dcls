from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .protocol import CoercerProtocol, CoercerSpawnerProtocol


class HubCoercer(CoercerProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        spawner: CoercerSpawnerProtocol

        def build(self) -> HubCoercer:
            return HubCoercer(self)

    def __init__(self, args: Args) -> None:
        self.worker = args.spawner(self)

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        result = self.worker(value=value, dtype=dtype)
        if result is not None:
            return result.value
        raise TypeError({"value": value, "expected_type": str(dtype)})


__all__ = ["HubCoercer"]
