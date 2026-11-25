from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .protocol import (
    TypeDescriberProtocol,
    TypeDescriberSpawnerProtocol,
    TypeDescriberWorkerProtocol,
)


@dataclass(kw_only=True, frozen=True)
class HubTypeDescriber(TypeDescriberProtocol):
    spawner: TypeDescriberSpawnerProtocol

    def __call__(self, *, dtype: Any) -> dict[str, Any]:
        worker: TypeDescriberWorkerProtocol

        def _hub(*, dtype: Any) -> dict[str, Any]:
            result = worker(dtype=dtype)
            if result is not None:
                return result.schema
            raise TypeError({"dtype": str(dtype)})

        worker = self.spawner(_hub)
        return _hub(dtype=dtype)


__all__ = ["HubTypeDescriber"]
