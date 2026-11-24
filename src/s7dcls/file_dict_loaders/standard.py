from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mechanism import JsonFileDictLoader, TomlFileDictLoader
from .ops import FirstMatchFileDictLoader
from .protocol import FileDictLoaderProtocol, StrictFileDictLoaderProtocol
from .scaffold import ScaffoldFileDictLoader


class StandardFileDictLoader(StrictFileDictLoaderProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        loaders: Sequence[FileDictLoaderProtocol] = (
            JsonFileDictLoader(),
            TomlFileDictLoader(),
        )

        def build(self) -> StandardFileDictLoader:
            return StandardFileDictLoader(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardFileDictLoader.Args()
        self.parent = ScaffoldFileDictLoader(
            loader=FirstMatchFileDictLoader(loaders=tuple(active_args.loaders))
        )

    def __call__(self, file: Path, /) -> dict[str, Any]:
        return self.parent(file)


__all__ = ["StandardFileDictLoader"]
