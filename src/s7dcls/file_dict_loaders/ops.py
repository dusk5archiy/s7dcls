from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .protocol import FileDictLoaderProtocol


@dataclass(kw_only=True, frozen=True)
class FirstMatchFileDictLoader(FileDictLoaderProtocol):
    loaders: Sequence[FileDictLoaderProtocol]

    def __call__(self, file: Path, /) -> dict[str, Any] | None:
        for loader in self.loaders:
            result = loader(file)
            if result is not None:
                return result
        return None


__all__ = ["FirstMatchFileDictLoader"]
