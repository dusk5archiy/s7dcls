from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from s7dcls.dict_transforms.mechanism import (
    KeyGateDictTransform,
    KeyPathDictTransform,
)
from s7dcls.file_dict_loaders.standard import StandardFileDictLoader
from s7dcls.string_manipulations.string_gates.protocol import StringGateProtocol

from .mechanism import RawFileDictFetcher, RawShellDictFetcher
from .ops import DecoratedDictFetcher
from .protocol import DictFetcherProtocol


class StandardShellDictFetcher(DictFetcherProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        key_gate: StringGateProtocol | None = None

        def build(self) -> StandardShellDictFetcher:
            return StandardShellDictFetcher(self)

    def __init__(self, args: Args | None = None) -> None:
        active_args = args or StandardShellDictFetcher.Args()
        fetcher: DictFetcherProtocol = RawShellDictFetcher()
        if active_args.key_gate is not None:
            fetcher = DecoratedDictFetcher(
                dict_fetcher=fetcher,
                dict_transform=KeyGateDictTransform(key_gate=active_args.key_gate),
            )
        self.parent = fetcher

    def __call__(self) -> dict[str, Any]:
        return dict(self.parent())


class StandardFileDictFetcher(DictFetcherProtocol):
    @dataclass(kw_only=True, frozen=True)
    class Args:
        file: Path
        key_path: Sequence[str] = ()
        key_gate: StringGateProtocol | None = None

        def build(self) -> StandardFileDictFetcher:
            return StandardFileDictFetcher(self)

    def __init__(self, args: Args) -> None:
        fetcher: DictFetcherProtocol = RawFileDictFetcher(
            file=args.file,
            loader=StandardFileDictLoader.Args().build(),
        )
        if args.key_path:
            fetcher = DecoratedDictFetcher(
                dict_fetcher=fetcher,
                dict_transform=KeyPathDictTransform(key_path=args.key_path),
            )
        if args.key_gate is not None:
            fetcher = DecoratedDictFetcher(
                dict_fetcher=fetcher,
                dict_transform=KeyGateDictTransform(key_gate=args.key_gate),
            )
        self.parent = fetcher

    def __call__(self) -> dict[str, Any]:
        return dict(self.parent())


__all__ = [
    "StandardFileDictFetcher",
    "StandardShellDictFetcher",
]
