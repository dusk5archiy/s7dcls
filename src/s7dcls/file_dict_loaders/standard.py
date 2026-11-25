from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mechanism import JsonFileDictLoaderWorker, TomlFileDictLoaderWorker
from .ops import FirstMatchFileDictLoaderWorker
from .protocol import FileDictLoaderProtocol, FileDictLoaderWorkerProtocol
from .scaffold import ScaffoldFileDictLoader


class StandardFileDictLoader(FileDictLoaderProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        loaders: Sequence[FileDictLoaderWorkerProtocol] = (
            JsonFileDictLoaderWorker(),
            TomlFileDictLoaderWorker(),
        )

        def build(self) -> StandardFileDictLoader:
            return StandardFileDictLoader(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardFileDictLoader.Args()
        self.parent = ScaffoldFileDictLoader(
            worker=FirstMatchFileDictLoaderWorker(workers=tuple(active_args.loaders))
        )

    def __call__(self, file: Path, /) -> dict[str, Any]:
        return self.parent(file)


__all__ = ["StandardFileDictLoader"]
