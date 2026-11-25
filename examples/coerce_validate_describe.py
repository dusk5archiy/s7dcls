from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from s7dcls import (
    AnyValueChecker,
    Gt,
    Lt,
    StandardJsonCoercer,
    StandardJsonSchemaDescriber,
    StandardTypeDescriber,
    StandardValidator,
)


@dataclass(kw_only=True, frozen=True)
class Config:
    root: Path
    port: Annotated[int, Gt(limit=0)] = 8000


def main() -> None:
    coercer = StandardJsonCoercer.Args().build()
    validator = StandardValidator.Args().build()
    describer = StandardTypeDescriber.Args().build()
    json_schema_describer = StandardJsonSchemaDescriber.Args().build()

    ports = coercer(value=[80, 443], dtype=tuple[int, ...])
    validator(
        value=-5,
        dtype=Annotated[int, AnyValueChecker(checkers=(Lt(limit=0), Gt(limit=10)))],
    )
    schema = describer(dtype=Config)
    json_schema = json_schema_describer(dtype=Config)

    assert ports == (80, 443)
    assert schema["type"] == "dataclass"
    assert json_schema["type"] == "object"
    print(ports)
    print(json_schema)


if __name__ == "__main__":
    main()
