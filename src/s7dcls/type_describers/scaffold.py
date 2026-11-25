from __future__ import annotations

from typing import Any

from .protocol import TypeDescriberProtocol, TypeDescriberSpawnerProtocol


class HubTypeDescriber(TypeDescriberProtocol):
    def __init__(self, *, spawner: TypeDescriberSpawnerProtocol) -> None:
        self.worker = spawner(self)

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        result = self.worker(dtype=dtype)
        if result is not None:
            return result.schema
        raise TypeError({"dtype": str(dtype)})


__all__ = ["HubTypeDescriber"]
