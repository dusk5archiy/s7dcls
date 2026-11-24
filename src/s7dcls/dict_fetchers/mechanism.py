from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from s7dcls.file_dict_loaders.mechanism import load_json_dict, load_toml_dict
from s7dcls.file_dict_loaders.protocol import StrictFileDictLoaderProtocol

from .protocol import DictFetcherProtocol


@dataclass(kw_only=True, frozen=True)
class RawShellDictFetcher(DictFetcherProtocol):
    def __call__(self) -> dict[str, str]:
        return dict(os.environ.items())


@dataclass(kw_only=True, frozen=True)
class RawFileDictFetcher(DictFetcherProtocol):
    file: Path
    loader: StrictFileDictLoaderProtocol

    def __call__(self) -> dict[str, Any]:
        return self.loader(self.file)


@dataclass(kw_only=True, frozen=True)
class RawJsonDictFetcher(DictFetcherProtocol):
    file: Path

    def __call__(self) -> dict[str, Any]:
        return load_json_dict(self.file)


@dataclass(kw_only=True, frozen=True)
class RawTomlDictFetcher(DictFetcherProtocol):
    file: Path

    def __call__(self) -> dict[str, Any]:
        return load_toml_dict(self.file)


__all__ = [
    "RawFileDictFetcher",
    "RawJsonDictFetcher",
    "RawShellDictFetcher",
    "RawTomlDictFetcher",
]
