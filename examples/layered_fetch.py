from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from s7dcls import (
    AggregateDataclassSource,
    Gt,
    NoCasePrefixGate,
    ScaffoldDataclassFetcher,
    StandardDataclassSource,
    StandardFileDictFetcher,
    StandardShellDictFetcher,
    StandardStringCoercer,
)


@dataclass(kw_only=True, frozen=True)
class Config:
    root: Path
    port: Annotated[int, Gt(limit=0)] = 8000


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        toml_file = Path(tmp) / "config.toml"
        toml_file.write_text(
            '[app]\nroot = "/var/run"\nport = 8000\n', encoding="utf-8"
        )

        os.environ["__APP__port"] = "9090"
        try:
            source = AggregateDataclassSource(
                sources=(
                    StandardDataclassSource.Args(
                        dict_fetcher=StandardFileDictFetcher.Args(
                            file=toml_file,
                            key_path=("app",),
                        ).build(),
                    ).build(),
                    StandardDataclassSource.Args(
                        dict_fetcher=StandardShellDictFetcher.Args(
                            key_gate=NoCasePrefixGate(prefix="__APP__"),
                        ).build(),
                        coercer=StandardStringCoercer.Args().build(),
                    ).build(),
                )
            )
            cfg = ScaffoldDataclassFetcher(source=source)(datacls=Config)
        finally:
            os.environ.pop("__APP__port", None)

    assert cfg == Config(root=Path("/var/run"), port=9090)
    print(cfg)


if __name__ == "__main__":
    main()
