from __future__ import annotations

from typing import Any

from .protocol import CoercerProtocol, CoercerSpawnerProtocol


class HubCoercer(CoercerProtocol):
    def __init__(self, *, spawner: CoercerSpawnerProtocol) -> None:
        self.worker = spawner(self)

    def __call__(self, *, value: Any, dtype: Any) -> Any:
        result = self.worker(value=value, dtype=dtype)
        if result is not None:
            return result.value
        raise TypeError({"value": value, "expected_type": str(dtype)})


__all__ = ["HubCoercer"]
