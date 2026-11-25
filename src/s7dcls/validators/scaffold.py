from __future__ import annotations

from typing import Any

from .protocol import ValidatorProtocol, ValidatorSpawnerProtocol


class HubValidator(ValidatorProtocol):
    def __init__(self, *, spawner: ValidatorSpawnerProtocol) -> None:
        self.worker = spawner(self)

    def __call__(self, *, value: Any, dtype: Any) -> None:
        result = self.worker(value=value, dtype=dtype)
        if result is not None:
            return
        raise TypeError({"value": value, "expected_type": str(dtype)})


__all__ = ["HubValidator"]
