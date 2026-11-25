from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class FileDictLoaderWorkerProtocol(Protocol):
    def __call__(self, file: Path, /) -> dict[str, Any] | None: ...


class FileDictLoaderProtocol(Protocol):
    def __call__(self, file: Path, /) -> dict[str, Any]: ...


__all__ = ["FileDictLoaderProtocol", "FileDictLoaderWorkerProtocol"]
