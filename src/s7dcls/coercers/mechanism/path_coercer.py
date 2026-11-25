from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from s7dcls.coercers.models import CoerceResult
from s7dcls.coercers.protocol import CoercerWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class PathCoercerWorker(CoercerWorkerProtocol):
    def __call__(self, *, value: Any, dtype: Any) -> CoerceResult[Path] | None:
        if dtype is not Path:
            return None

        if isinstance(value, (str, Path)):
            return CoerceResult(value=Path(value))

        raise TypeError(
            {
                "value": value,
                "expected_type": str(Path),
                "got_type": str(type(value)),
            }
        )


__all__ = ["PathCoercerWorker"]
