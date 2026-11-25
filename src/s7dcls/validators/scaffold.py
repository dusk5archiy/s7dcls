from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .protocol import ValidatorProtocol, ValidatorSpawnerProtocol


class HubValidator(ValidatorProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        spawner: ValidatorSpawnerProtocol

        def build(self) -> HubValidator:
            return HubValidator(self)

    def __init__(self, args: Args) -> None:
        self.worker = args.spawner(self)

    def __call__(self, *, value: Any, dtype: Any) -> None:
        result = self.worker(value=value, dtype=dtype)
        if result is not None:
            return
        raise TypeError({"value": value, "expected_type": str(dtype)})


__all__ = ["HubValidator"]
