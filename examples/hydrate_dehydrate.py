from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from s7dcls import (
    Gt,
    StandardDataclassDehydrator,
    StandardDataclassHydrator,
)


@dataclass(kw_only=True, frozen=True)
class Config:
    root: Path
    port: Annotated[int, Gt(limit=0)] = 8000


def main() -> None:
    hydrator = StandardDataclassHydrator.Args().build()
    dehydrator = StandardDataclassDehydrator.Args().build()

    cfg = hydrator(data={"root": "/var/run", "port": 8080}, datacls=Config)
    raw = dehydrator(instance=cfg)
    assert raw == {"root": "/var/run", "port": 8080}
    print(cfg)
    print(raw)


if __name__ == "__main__":
    main()
