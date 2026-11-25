from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeGuard

from .protocol import FileDictLoaderWorkerProtocol


def is_str_key_dict(obj: Any) -> TypeGuard[dict[str, Any]]:
    return isinstance(obj, dict) and all(isinstance(k, str) for k in obj)


def load_json_dict(file: Path, /) -> dict[str, Any]:
    if not file.is_file():
        return {}
    obj = json.loads(file.read_text(encoding="utf-8"))
    if not is_str_key_dict(obj):
        raise ValueError(
            {
                "file": file,
                "expected_type": str(dict[str, Any]),
                "got_type": str(type(obj)),
            }
        )
    return obj


def load_toml_dict(file: Path, /) -> dict[str, Any]:
    if not file.is_file():
        return {}
    obj = tomllib.loads(file.read_text(encoding="utf-8"))
    if not is_str_key_dict(obj):
        raise ValueError(
            {
                "file": file,
                "expected_type": str(dict[str, Any]),
                "got_type": str(type(obj)),
            }
        )
    return obj


@dataclass(kw_only=True, frozen=True)
class JsonFileDictLoaderWorker(FileDictLoaderWorkerProtocol):
    suffixes: tuple[str, ...] = (".json",)

    def __call__(self, file: Path, /) -> dict[str, Any] | None:
        if file.suffix.lower() not in self.suffixes:
            return None
        return load_json_dict(file)


@dataclass(kw_only=True, frozen=True)
class TomlFileDictLoaderWorker(FileDictLoaderWorkerProtocol):
    suffixes: tuple[str, ...] = (".toml",)

    def __call__(self, file: Path, /) -> dict[str, Any] | None:
        if file.suffix.lower() not in self.suffixes:
            return None
        return load_toml_dict(file)


__all__ = [
    "JsonFileDictLoaderWorker",
    "TomlFileDictLoaderWorker",
    "is_str_key_dict",
    "load_json_dict",
    "load_toml_dict",
]
