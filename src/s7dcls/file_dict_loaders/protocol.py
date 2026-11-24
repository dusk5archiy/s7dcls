from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class FileDictLoaderProtocol(Protocol):
    def __call__(self, file: Path, /) -> dict[str, Any] | None: ...


class StrictFileDictLoaderProtocol(Protocol):
    def __call__(self, file: Path, /) -> dict[str, Any]: ...


__all__ = ["FileDictLoaderProtocol", "StrictFileDictLoaderProtocol"]
