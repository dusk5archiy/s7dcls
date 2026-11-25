from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .protocol import FileDictLoaderProtocol, FileDictLoaderWorkerProtocol


@dataclass(kw_only=True, frozen=True)
class ScaffoldFileDictLoader(FileDictLoaderProtocol):
    worker: FileDictLoaderWorkerProtocol

    def __call__(self, file: Path, /) -> dict[str, Any]:
        result = self.worker(file)
        if result is not None:
            return result
        raise ValueError({"file": file, "suffix": file.suffix.lower()})


__all__ = ["ScaffoldFileDictLoader"]
