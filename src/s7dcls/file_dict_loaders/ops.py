from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .protocol import FileDictLoaderWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchFileDictLoaderWorker(FileDictLoaderWorkerProtocol):
    workers: Sequence[FileDictLoaderWorkerProtocol]

    def __call__(self, file: Path, /) -> dict[str, Any] | None:
        for worker in self.workers:
            result = worker(file)
            if result is not None:
                return result
        return None


__all__ = ["FirstMatchFileDictLoaderWorker"]
